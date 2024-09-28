import asyncio
import aiofiles
import os
import logging
import base64

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputFile, FSInputFile
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENTS_TOKEN = os.getenv('PAYMASTER_TOKEN')
CONTACT = os.getenv('CONTACT')
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=200*100)  # в копейках (руб.)


# log
logging.basicConfig(level=logging.INFO)

# init
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


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
    await message.answer("Добро пожаловать! Выберите команду:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "Инструкция по установке")
async def help_command(message: Message, state: FSMContext):
    text = f'''
1. Установите WireGuard
[Официальная ссылка](https://www.wireguard.com/install/)
2. Импортируйте файл конфигурации
3. Запустите WireGuard
'''
    await message.answer(text, parse_mode='Markdown')
    await message.answer_photo(FSInputFile(path='photos/0.png'), caption="Шаг 1: Установка WireGuard")
    await message.answer_photo(FSInputFile(path='photos/1.jpg'), caption="Шаг 2: Настройка конфигурации")
    await message.answer_photo(FSInputFile(path='photos/2.png'), caption="Шаг 3: Запуск WireGuard")


@dp.message(lambda message: message.text == "Контакты")
async def contacts(message: Message):
    text = f'''
    С вопросами о работе бота обращаться к @{CONTACT}
    '''
    await message.answer(text)


@dp.message(lambda message: message.text == "О боте")
async def about(message: Message):
    text = '''
    👋 Привет! Мы - команда разработчиков из Москвы. 
Наша задача - обеспечить свободную сеть в родной стране за доступный прайс для каждого. Серверы находятся в Латвии, что обеспечивает максимальную скорость передачи трафика 🚀
    
💳 Подписка составляет 200 руб/мес. Оплату можно производить в боте, либо написав лично нам.  
    
Ваша команда начос. 🌝
    '''
    await message.answer(text)


@dp.message(lambda message: message.text == "Купить подписку")
async def buy(message: types.Message):
    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж.")

    await bot.send_invoice(message.chat.id,
                           title="Подписка на VPN",
                           description="Активация подписки VPN на 1 месяц",
                           provider_token=PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://images.everyeye.it/img-notizie/lego-super-mario-il-potente-bowser-offerta-amazon-prezzo-prima-v3-745290-800x600.webp",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


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
        await bot.send_message(message.chat.id,
                               f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно.")
        # Тут должен быть кусок с отправкой конфига
    else:
        print(f'Что-то пошло не так. Информамция о покупке - {payment}')
        await bot.send_message(message.chat.id,
                               f'Что-то пошло не так. Обратитесь в поддержку. Ответ - {payment}')


# echo bot
@dp.message(F.text)
async def echo(message: types.Message):
    await message.answer(message.text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
