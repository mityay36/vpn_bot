import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InputMediaPhoto
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
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Для ПК",
        callback_data="instructions_pc")
    )
    builder.add(types.InlineKeyboardButton(
        text="Для мобильного устройства",
        callback_data="instructions_mobile")
    )
    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        "Выберите тип устройства:", reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "instructions_pc")
async def installation_guide(callback: types.CallbackQuery):
    text = f'''
1. Установите WireGuard
[Официальная ссылка]({config.URL})
2. Импортируйте файл конфигурации
3. Запустите WireGuard
'''
    await callback.message.answer(text, parse_mode='Markdown')
    await callback.message.answer_photo(
        FSInputFile(path='photos/for_pc/0.png'),
        caption="Шаг 1: Установка WireGuard"
    )
    await callback.message.answer_photo(
        FSInputFile(path='photos/for_pc/1.jpg'),
        caption="Шаг 2: Настройка конфигурации"
    )
    await callback.message.answer_photo(
        FSInputFile(path='photos/for_pc/2.png'),
        caption="Шаг 3: Запуск WireGuard"
    )

@dp.callback_query(F.data == "instructions_mobile")
async def installation_guide(callback: types.CallbackQuery):
    text = f'''
1. Установите WireGuard в *AppStore* или *Play Market*
2. Импортируйте файл конфигурации
3. Запустите WireGuard
'''
    await callback.message.answer(text, parse_mode='Markdown')
    media = [
        InputMediaPhoto(media=FSInputFile(path='photos/for_mobile/1.jpg'),caption="Шаг 1: Откройте файл с туннелем"),
        InputMediaPhoto(media=FSInputFile(path='photos/for_mobile/2.jpg')),
    ]
    await callback.message.answer_media_group(media)

    media2 = [
        InputMediaPhoto(media=FSInputFile(path='photos/for_mobile/3.jpg'),caption="Шаг 2: Импортируйте конфиг"),
        InputMediaPhoto(media=FSInputFile(path='photos/for_mobile/4.jpg')),
    ]

    await callback.message.answer_media_group(media2)

    await callback.message.answer_photo(
        FSInputFile(path='photos/for_mobile/5.jpg'),
        caption="Шаг 3: Запустите VPN"
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
    доступный прайс для каждого. Серверы находятся в Латвии и Молдове, что \
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
        callback_data="choose_tunnel")
    )
    builder.add(types.InlineKeyboardButton(
        text="Купить новый",
        callback_data="new_buy")
    )
    await message.answer(
        "Вы хотите продлить подписку или приобрести новый конфиг?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "choose_tunnel")
async def extend_buy_options(callback: types.CallbackQuery, state: FSMContext):

    tunnel_list = await get_tunnel_list(callback.from_user.username)
    
    if not tunnel_list:
        await callback.message.answer("Для проверки статуса платежа необходимо купить туннель.")
        return
    
    text = 'Выберете номер конфига, который хотите продлить: \n'
    
    builder = InlineKeyboardBuilder()
    for num, tunnel in enumerate(tunnel_list):
        text += ''.join(
            f'{num + 1}. {tunnel[0]}  |  Статус -'
            f'{tunnel[1]}\n'
        )
        # допилить, чтобы по 3 в линию
        builder.add(types.InlineKeyboardButton(
            text=f"{num + 1}",
            callback_data=f"extend_buy:{tunnel[0]}")
        )

        builder.adjust(3)

    await callback.message.answer(text, reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("extend_buy:"))
async def extend_buy_process(callback: types.CallbackQuery, state: FSMContext):
    # необходимо допилить логику с продлением конфигурации. Заново конфиг отсылать смысла нет.
    
    config_name = callback.data.split(":")[1]

    await state.update_data(config_name=config_name)
    await state.update_data(buy_type='2')

    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Продлить подписку",
        callback_data="buy")
    )
    await callback.message.answer(f"Вы выбрали конфиг '{config_name}' для продления.", reply_markup=builder.as_markup())


    # Отправляем информацию об оплате
    # builder = InlineKeyboardBuilder()
    # builder.add(types.InlineKeyboardButton(
    #     text="Проверка платежа",
    #     callback_data="check_payment")
    # )
    # await callback.message.answer("Нажмите 'Проверка платежа' после завершения оплаты.", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "new_buy")
async def process_new_buy(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(buy_type='1')
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Приобрести подписку",
        callback_data="buy")
    )
    await callback.message.answer(f"Вы выбрали покупку нового конфига.", reply_markup=builder.as_markup())



@dp.callback_query(F.data == "buy")
async def process_payment(callback: types.CallbackQuery, state: FSMContext):

    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(callback.message.chat.id, "Тестовый платеж.")

    await state.update_data(new_buy_state=0)
    # получаем данные о состоянии
    data = await state.get_data()
    payment_id = data.get("payment_id")
    if payment_id:
        payment_info = Payment.find_one(payment_id)
        status = payment_info.status
    
        # проверяем статус платежа
        if status in {"succeeded", "canceled"}:
            payment = get_payment()
        else:
            payment = payment_info
    else: 
        payment = get_payment()

    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']

    await state.update_data(payment_id=payment_id)

    payment_url = (payment_data['confirmation'])['confirmation_url']
    text = f"""Произведите оплату по ссылке:\
    {payment_url} \

        
При проблемах с оплатой обращайтесь к администратору.
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
    config_name = data.get("config_name")
    buy_type= data.get("buy_type")



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
            if buy_type == '1':
                perm_state = await state.get_data()
                payment_status = perm_state.get('new_buy_state')

                if payment_info.paid:
                    if payment_status == 0:
                        await bot.send_message(callback.message.chat.id, 'Первичная отправка конфига')
                        
                        # Логика формирования и выдачи конфига юзеру
                        ans_json = await (get_data(
                            f"{os.getenv('SET_PEER')}/{callback.from_user.username}"))
                        file = await get_file_from_data(callback.from_user.username, ans_json)
                        await callback.message.answer_document(FSInputFile(path=f"configs/{file}.conf"))
                        await state.update_data(new_buy_state=1)
                        await state.update_data(buy_type="0")

                    else:
                        await bot.send_message(callback.message.chat.id, 'Ищите конфиг выше :^)')
                        # здесь логика повторной отправки последнего купленного конфига
            elif buy_type == '2':
                perm_state = await state.get_data()
                payment_status = data.get('new_buy_state')

                if payment_info.paid:
                    if payment_status == 0:

                        # логика продления выбранного конфига
                        ans_json = await (get_data(
                            f"{config.EXTEND_PEER}/{config_name.split('-')[0]}"))
                        
                        if ans_json['Message'].startswith('1 Month added successfully'):
                            await bot.send_message(callback.message.chat.id, 'Туннель успешно продлен!')
                        else:
                            await bot.send_message(callback.message.chat.id, 'Если Вы видите данное ообщение, сообщите администратору :/')
                        
                        await state.update_data(buy_type="0")
                        await state.update_data(new_buy_state=1)


                    else:
                        await bot.send_message(callback.message.chat.id, 'Ищите инфу выше :^)')


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
