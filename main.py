import asyncio
import json
import logging
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yookassa import Payment, Configuration

import config
from logic import get_tunnel_list

# log
logging.basicConfig(level=logging.INFO)

# init
bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()

Configuration.account_id = config.MARKET_ID
Configuration.secret_key = config.YOKASSA_API_KEY


async def create_payment(price):
    await Payment.create({
        "amount": {
            "value": price+'.00',
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "sberbank",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/vpnachos_bot"
        },
        "description": "Заказ №72"
    }, str(uuid.uuid4()))


@dp.message(Command("start"))
async def start_command(message: Message):
    # Создаем кнопки
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить подписку")],
            [KeyboardButton(text="Контакты"), KeyboardButton(text="О боте")],
            [KeyboardButton(text="Инструкция по установке")]
        ],
        resize_keyboard=True
    )

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        "Добро пожаловать! Выберите команду:", reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "Инструкция по установке")
async def help_command(message: Message, state: FSMContext):
    text = f'''
1. Установите WireGuard
[Официальная ссылка]({config.URL})
2. Импортируйте файл конфигурации
3. Запустите WireGuard
'''
    await message.answer(text, parse_mode='Markdown')
    await message.answer_photo(
        FSInputFile(path='photos/0.png'),
        caption="Шаг 1: Установка WireGuard"
    )
    await message.answer_photo(
        FSInputFile(path='photos/1.jpg'),
        caption="Шаг 2: Настройка конфигурации"
    )
    await message.answer_photo(
        FSInputFile(path='photos/2.png'),
        caption="Шаг 3: Запуск WireGuard"
    )


@dp.message(lambda message: message.text == "Контакты")
async def contacts(message: Message):
    text = f'''
    С вопросами о работе бота обращаться к @{config.CONTACT}
    '''
    await message.answer(text)


@dp.message(lambda message: message.text == "О боте")
async def about(message: Message):
    text = f'''
👋 Привет! Мы - команда разработчиков из Москвы.
Наша задача - обеспечить свободную сеть в родной стране за \
доступный прайс для каждого. Серверы находятся в Латвии, что \
обеспечивает максимальную скорость передачи трафика 🚀

💳 Подписка составляет {config.PRICE} руб/мес. Оплата \
производится через SberPay в формате пуш уведомления. 

Ваша команда начос. 🌝
    '''
    await message.answer(text)


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment = message.successful_payment
    if payment:
        payment_info = message.successful_payment.as_dict()
        for k, v in payment_info.items():
            print(f"{k} = {v}")
        await bot.send_message(
            message.chat.id,
            f"Платеж на сумму {message.successful_payment.total_amount // 100}\
{message.successful_payment.currency} прошел успешно."
        )

        # Тут должен быть кусок с отправкой конфига или его продлением.

        await bot.send_message(message.chat.id, 'Пу-пу-пу...')
    else:
        print(f'Что-то пошло не так. Информамция о покупке - {payment}')
        await bot.send_message(
            message.chat.id,
            f'Что-то пошло не так. Обратитесь в поддержку. Ответ - {payment}'
        )


@dp.message(lambda message: message.text == "Купить подписку")
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Продлить",
        callback_data="extend_buy")
    )
    builder.add(types.InlineKeyboardButton(
        text="Купить новый",
        callback_data="new_buy")
    )
    await message.answer(
        "Вы хотите продлить подписку или приобрести новый конфиг?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "extend_buy")
async def send_random_value(callback: types.CallbackQuery):
    # тут должен быть запрос к API для получения кол-ва туннелей пользователя
    # представим, что запрос прошел и мы получили tunnel_list

    # tunnel_list = [(name1, status1), (name2, status2), ...]
    tunnel_list = get_tunnel_list(callback.message.chat.id)
    text = 'Выберете номер конфига, который хотите продлить: \n'
    alive_emoji = '🟢'
    dead_emoji = '🔴'
    builder = InlineKeyboardBuilder()
    for num, tunnel in enumerate(tunnel_list):
        text += ''.join(
            f'{num + 1}. {tunnel[0]}  |  Статус -\
{alive_emoji if tunnel[1] == "alive" else dead_emoji}\n'
        )
        # допилить, чтобы по 3 в линию
        builder.add(types.InlineKeyboardButton(
            text=f"{num + 1}",
            callback_data="extend_buy_2")
        )

    await callback.message.answer(text, reply_markup=builder.as_markup())


@dp.callback_query(F.data == "new_buy")
async def process_payment(callback: types.CallbackQuery, state: FSMContext):
    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(callback.message.chat.id, "Тестовый платеж.")
    payment = Payment.create({
        "amount": {
            "value": str(config.PRICE) + '.00',
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/vpnachos_bot"
        },
        "capture": "true",
        "description": "Месяц подписки"
    }, str(uuid.uuid4()))
    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    await state.update_data(payment_id=payment_id)

    payment_url = (payment_data['confirmation'])['confirmation_url']
    text = f"""Произведите оплату по ссылке:\
    {payment_url} \
    
    Ссылка доступна 10 минут.
    """
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Проверка платежа",
        callback_data="check_payment")
    )
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=builder.as_markup())


@dp.callback_query(F.data == "check_payment")
async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    # Получаем payment_id из состояния
    data = await state.get_data()
    payment_id = data.get("payment_id")

    if not payment_id:
        await bot.send_message(callback.message.chat.id, "Не найден идентификатор платежа.")
        return

    # Пытаемся получить информацию о платеже
    try:
        payment_info = Payment.find_one(payment_id)

        if payment_info.status == "succeeded":
            await bot.send_message(
                callback.message.chat.id,
                "Ваш платеж прошел успешно! Спасибо за покупку."
            )

            # Тут можно отправить конфиг или продлить услугу
            # Пример:
            # await send_vpn_config(callback.message.chat.id)
            await bot.send_message(callback.message.chat.id, 'Пу-пу-пу...')

        elif payment_info.status in ["pending", "waiting_for_capture"]:
            await bot.send_message(
                callback.message.chat.id,
                "Платеж еще обрабатывается, пожалуйста, подождите несколько секунд."
            )
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=str(payment_info.status)
            )
        else:
            await bot.send_message(
                callback.message.chat.id,
                f"Платеж не был успешным. Статус: {payment_info.status}. Обратитесь в поддержку."
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке платежа: {e}")
        await bot.send_message(
            callback.message.chat.id,
            "Произошла ошибка при проверке платежа. Попробуйте позже."
        )


# echo bot
@dp.message(F.text)
async def echo(message: types.Message):
    await message.answer(message.text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
