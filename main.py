import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yookassa import Payment, Configuration

import config
from logic import get_tunnel_list, get_payment, get_data, get_file_from_data


# log
logging.basicConfig(level=logging.INFO)

# init
bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()

Configuration.account_id = config.MARKET_ID
Configuration.secret_key = config.YOKASSA_API_KEY


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
async def installation_guide(message: Message):
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
    👋 Привет! Мы - команда разработчиков из Москвы.\n
Наша задача - обеспечить свободную сеть в родной стране за \
    доступный прайс для каждого. Серверы находятся в Латвии, что \
    обеспечивает максимальную скорость передачи трафика 🚀\
    \n
💳 Подписка составляет {config.PRICE} руб/мес. Оплата производится \
    через Юмани в формате всплывающего окна.

Ваша команда начос. 🌝
    '''
    await message.answer(text)


@dp.message(lambda message: message.text == "Купить подписку")
async def pay_options(message: types.Message):
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
async def extend_buy_options(callback: types.CallbackQuery, state: FSMContext):

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
            f'{num + 1}. {tunnel[0]}  |  Статус -'
            f'{alive_emoji if tunnel[1] == "alive" else dead_emoji}\n'
        )
        # допилить, чтобы по 3 в линию
        builder.add(types.InlineKeyboardButton(
            text=f"{num + 1}",
            callback_data="extend_buy_2")
        )

    await callback.message.answer(text, reply_markup=builder.as_markup())


@dp.callback_query(F.data == "extend_buy_2")
async def extend_buy_process(callback: types.CallbackQuery, state: FSMContext):
    ...


@dp.callback_query(F.data == "new_buy")
async def process_payment(callback: types.CallbackQuery, state: FSMContext):

    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(callback.message.chat.id, "Тестовый платеж.")

    await state.update_data(new_buy_state=0)

    payment = get_payment()

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

            perm_state = await state.get_data()
            payment_status = perm_state.get('new_buy_state')

            if payment_info.paid:
                if payment_status == 0:
                    await bot.send_message(callback.message.chat.id, 'Первичная отправка конфига')
                    # Здесь должна быть некоторая логика формирования и выдачи конфига юзеру

                    ans_json = await (get_data(
                        f"{os.getenv('SET_PEER')}/{callback.from_user.id}+{callback.from_user.username}"))
                    file = await get_file_from_data(callback.from_user.username, ans_json)
                    await callback.message.answer_document(FSInputFile(path=f"configs/{file}.conf"))
                    await state.update_data(new_buy_state=1)
                else:
                    await bot.send_message(callback.message.chat.id, 'Ищите конфиг выше :^)')
                    # здесь логика повторной отправки последнего купленного конфига

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
