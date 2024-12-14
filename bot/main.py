import asyncio
import json
import logging
import os

import config
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (BotCommand, BotCommandScopeDefault, CallbackQuery,
                           FSInputFile, InlineKeyboardButton, InputMediaPhoto,
                           KeyboardButton, Message, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logic import get_data, get_file_from_data, get_payment, get_tunnel_list
from yookassa import Configuration, Payment

# from log import log_user_activity, UserContextFilter


# init
bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()

Configuration.account_id = config.MARKET_ID
Configuration.secret_key = config.YOKASSA_API_KEY


async def set_commands():
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/update", description="Обновить бота"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


@dp.message(Command("update"))
async def start_command(message: Message):

    await message.delete()

    if True:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Купить подписку")],
                [
                    KeyboardButton(text="Тех. Поддержка"),
                    KeyboardButton(text="О боте")
                ],
                [KeyboardButton(text="Инструкция по установке")]
            ],
            resize_keyboard=True
        )
        msg = await message.answer(
            "Бот успешно обновлен!", reply_markup=keyboard
        )
        await asyncio.sleep(config.SLEEP_TIME)

        await msg.delete()

    else:
        await message.answer("Обновлений нет")


@dp.message(Command("start"))
async def start_command(message: Message):

    await bot.send_message(
        config.ADMIN_ID_1,
        f'We have new user @{message.from_user.username}'
    )
    await bot.send_message(
        config.ADMIN_ID_2,
        f'We have new user @{message.from_user.username}'
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить подписку")],
            [
                KeyboardButton(text="Тех. Поддержка"),
                KeyboardButton(text="О боте")
            ],
            [KeyboardButton(text="Инструкция по установке")]
        ],
        resize_keyboard=True
    )
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Получить тестовый конфиг',
        callback_data='get_trial'
    ))

    hello_text = '''
🌐 Защитите свой интернет-трафик с Nachos Web! 🚀

🔒 Ваша безопасность — наш приоритет. \
Мы предоставляем ПО для туннелирования \
и шифрования интернет-трафика, чтобы вы \
могли работать и общаться в интернете, не \
беспокоясь о конфиденциальности.

💡 Почему Nachos?

→ Полная анонимность
→ Свобода без границ
→ Высокая скорость соединения
→ Современная криптография
→ Подходит для всех устройств


🔗 Не ждите, защитите себя прямо сейчас!
'''
    await message.answer(
        hello_text, reply_markup=builder.as_markup()
    )

    # await message.answer(
    #     "Выберите дальнейшую команду:", reply_markup=keyboard
    # )

    await message.answer(reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == 'get_trial')
async def get_trial_callback(callback: CallbackQuery):

    ans_json = await (
        get_data(
            f"""
{os.getenv('GET_TRIAL')}/{callback.from_user.username}+\
{callback.message.chat.id}
"""))
    if ans_json.startswith('Error'):
        await callback.message.answer(
            'У вас уже есть конфигурация :)'
        )
        return
    file = await get_file_from_data(
        callback.from_user.username, ans_json
    )
    await callback.message.answer_document(
        FSInputFile(path=f"configs/{file}.conf")
    )

    await callback.message.answer(
        "🎉 Вы получили тестовый доступ! \
Попробуйте наши функции в течение 3 дней.\n\n"
        "Если у вас есть вопросы, обратитесь \
в техподдержку. Будем рады помочь!🌝"
    )

    await bot.send_message(
        config.ADMIN_ID_1,
        f'Пользователь [@{callback.from_user.username}, \
{callback.message.chat.id}] активировал триал.'
    )
    await bot.send_message(
        config.ADMIN_ID_2,
        f'Пользователь [@{callback.from_user.username}, \
{callback.message.chat.id}] активировал триал.'
    )

    await callback.answer()


@dp.message(lambda message: message.text == "Инструкция по установке")
async def installation_guide(message: Message):

    await message.delete()

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Для ПК",
        callback_data="instructions_pc")
    )
    builder.add(InlineKeyboardButton(
        text="Для мобильного устройства",
        callback_data="instructions_mobile")
    )
    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        "Выберите тип устройства:", reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "instructions_pc")
async def installation_guide(callback: CallbackQuery):

    await callback.message.delete()

    text = f'''
1. Установите WireGuard \
[Официальная ссылка]({config.URL})
2. Импортируйте файл конфигурации
3. Запустите WireGuard
'''
    msg1 = await callback.message.answer(
        text,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    msg2 = await callback.message.answer_photo(
        FSInputFile(path=f'{config.PHOTO_DIR}/for_pc/0.png'),
        caption="Шаг 1: Установка WireGuard"
    )
    msg3 = await callback.message.answer_photo(
        FSInputFile(path=f'{config.PHOTO_DIR}/for_pc/1.jpg'),
        caption="Шаг 2: Настройка конфигурации"
    )
    msg4 = await callback.message.answer_photo(
        FSInputFile(path=f'{config.PHOTO_DIR}/for_pc/2.png'),
        caption="Шаг 3: Запуск WireGuard"
    )
    await asyncio.sleep(config.SLEEP_TIME)

    await msg1.delete()
    await msg2.delete()
    await msg3.delete()
    await msg4.delete()


@dp.callback_query(F.data == "instructions_mobile")
async def installation_guide(callback: CallbackQuery):

    await callback.message.delete()

    text = f'''
1. Установите WireGuard в \
[AppStore]({config.URL2}) или [Play Market]({config.URL3})
2. Импортируйте файл конфигурации
3. Запустите WireGuard
'''
    msg1 = await callback.message.answer(
        text,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    media = [
        InputMediaPhoto(
            media=FSInputFile(
                path=f'{config.PHOTO_DIR}/for_mobile/1.jpg'
            ),
            caption="Шаг 1: Откройте файл с туннелем"
        ),
        InputMediaPhoto(
            media=FSInputFile(
                path=f'{config.PHOTO_DIR}/for_mobile/2.jpg'
            )
        ),
    ]
    msg2 = await callback.message.answer_media_group(media)

    media2 = [
        InputMediaPhoto(
            media=FSInputFile(
                path=f'{config.PHOTO_DIR}/for_mobile/3.jpg'
            ),
            caption="Шаг 2: Импортируйте конфиг"
        ),
        InputMediaPhoto(
            media=FSInputFile(
                path=f'{config.PHOTO_DIR}/for_mobile/4.jpg'
            )
        ),
    ]

    msg3 = await callback.message.answer_media_group(media2)

    msg4 = await callback.message.answer_photo(
        FSInputFile(
            path=f'{config.PHOTO_DIR}/for_mobile/5.jpg'
        ),
        caption="Шаг 3: Запустите VPN"
    )

    await asyncio.sleep(config.SLEEP_TIME)

    await msg1.delete()
    for msg in msg2:
        await msg.delete()
    for msg in msg3:
        await msg.delete()
    await msg4.delete()


@dp.message(lambda message: message.text == "Тех. Поддержка")
async def contacts(message: Message):
    await message.delete()

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Контакты",
        callback_data="contacts")
    )
    builder.add(InlineKeyboardButton(
        text="FAQ",
        callback_data="questions")
    )
    await message.answer(
        "Выберите опцию:", reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "questions")
async def contacts(callback: CallbackQuery):

    await callback.message.delete()

    text = '''
    → *Почему одна конфигурация не работает на двух \
        устройствах одновременно?*\n
Это происходит, потому что так спроектирован WireGuard. \
Удаленный сервер должен знать \
от какого адресата ему ждать трафик. Каждое устройство, \
это отдельный адресат, следовательно, \
когда одна конфигурация используется на двух и более устройствах \
одновременно адресат меняется каждую секунду, и сервер \
не может целостно передать интернет из \
двух независимых каналов информации. \
Для каждого отдельного устройства мы рекомендуем использовать \
отдельные конфигурации во избежание конфликтов.\n
→ *Почему при переключение мобильной сети и WIFI интернет работает не сразу?*\n
Серверу нужно какое-то время (21 секунда), чтобы уловить новый \
изменившийся адресат и снова начать поддерживать стабильное \
соединение уже с нового адреса.\n
→ *У меня Android, не могу добавить туннель, что делать?*\n
Если у Вас возникает ошибка имени при добавлении конфигурации WireGuard, \
смените имя файла на более короткое (до 15 символов). Если проблема \
остается, напишите нам в техническую поддержку.
'''

    msg = await callback.message.answer(
        text,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

    await asyncio.sleep(config.SLEEP_TIME)
    await msg.delete()


@dp.callback_query(F.data == "contacts")
async def contacts(callback: CallbackQuery):
    logger.info(
        "Handling update",
        extra={
            'chat_id': callback.from_user.id,
            'username': callback.from_user.username or "NoUsername"
        }
    )

    await callback.message.delete()

    text = f'''
    С вопросами о работе бота обращаться к [@el_nachoss]({config.CONTACT}). \n
Новостной канал: [Nachos VPN News]({config.CONTACT_CHANELL})
'''

    msg = await callback.message.answer(
        text,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

    await asyncio.sleep(config.SLEEP_TIME)
    await msg.delete()


@dp.message(lambda message: message.text == "О боте")
async def about(message: Message):

    await message.delete()

    text = f'''
    👋 Привет! Мы - команда разработчиков из Москвы.\n
Наша задача - обеспечить свободную сеть в родной стране за \
доступный прайс для каждого. Серверы находятся в Латвии и Молдове, что \
обеспечивает максимальную скорость передачи трафика 🚀\n
💳 Подписка составляет {config.PRICE} руб/мес. Оплата производится \
через Юмани банковской картой.\n
Ваша команда начос. 🌝
    '''

    msg = await message.answer(text)
    await asyncio.sleep(config.SLEEP_TIME)
    await msg.delete()


@dp.message(lambda message: message.text == "Купить подписку")
async def pay_options(message: Message):

    await message.delete()

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Продлить",
        callback_data="choose_tunnel")
    )
    builder.add(InlineKeyboardButton(
        text="Купить новый",
        callback_data="new_buy")
    )
    await message.answer(
        "Вы хотите продлить подписку или приобрести новый конфиг?",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "choose_tunnel")
async def extend_buy_options(callback: CallbackQuery, state: FSMContext):

    await callback.message.delete()

    tunnel_list = await get_tunnel_list(callback.from_user.username)

    if not tunnel_list:
        await callback.message.answer(
            "Для проверки статуса платежа необходимо купить туннель."
        )
        return

    text = 'Выберете номер конфига, который хотите продлить: \n'

    builder = InlineKeyboardBuilder()
    for num, tunnel in enumerate(tunnel_list):
        text += ''.join(
            f'{num + 1}. {tunnel[0]}  |  Статус -'
            f'{tunnel[1]}\n'
        )
        # допилить, чтобы по 3 в линию
        builder.add(InlineKeyboardButton(
            text=f"{num + 1}",
            callback_data=f"extend_buy:{tunnel[0]}")
        )

        builder.adjust(3)

    await callback.message.answer(text, reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("extend_buy:"))
async def extend_buy_process(callback: CallbackQuery, state: FSMContext):
    # необходимо допилить логику с продлением конфигурации.
    # Заново конфиг отсылать смысла нет.

    await callback.message.delete()

    config_name = callback.data.split(":")[1]

    await state.update_data(config_name=config_name)
    await state.update_data(buy_type='2')

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Продлить подписку",
        callback_data="buy")
    )
    await callback.message.answer(
        f"Вы выбрали конфиг '{config_name}' для продления.",
        reply_markup=builder.as_markup()
    )

    # Отправляем информацию об оплате
    # builder = InlineKeyboardBuilder()
    # builder.add(InlineKeyboardButton(
    #     text="Проверка платежа",
    #     callback_data="check_payment")
    # )
    # await callback.message.answer(
    # "Нажмите 'Проверка платежа' после завершения оплаты.",
    # reply_markup=builder.as_markup()
    # )


@dp.callback_query(F.data == "new_buy")
async def process_new_buy(callback: CallbackQuery, state: FSMContext):

    await callback.message.delete()

    await state.update_data(buy_type='1')
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Приобрести подписку",
        callback_data="buy")
    )
    await callback.message.answer(
        "Вы выбрали покупку нового конфига.",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "buy")
async def process_payment(callback: CallbackQuery, state: FSMContext):

    await callback.message.delete()

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
    builder.add(InlineKeyboardButton(
        text="Проверка платежа",
        callback_data="check_payment")
    )
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=builder.as_markup())


@dp.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery, state: FSMContext):
    # Получаем payment_id из состояния
    data = await state.get_data()
    payment_id = data.get("payment_id")
    config_name = data.get("config_name")
    buy_type = data.get("buy_type")

    if not payment_id:
        await bot.send_message(
            callback.message.chat.id,
            "Не найден идентификатор платежа."
        )
        return

    # Пытаемся получить информацию о платеже
    try:
        payment_info = Payment.find_one(payment_id)

        if payment_info.status == "succeeded":
            msg1 = await bot.send_message(
                callback.message.chat.id,
                "Ваш платеж прошел успешно! Спасибо за покупку."
            )
            if buy_type == '1':
                perm_state = await state.get_data()
                payment_status = perm_state.get('new_buy_state')

                if payment_info.paid:
                    if payment_status == 0:

                        await callback.message.delete()

                        msg2 = await bot.send_message(
                            callback.message.chat.id,
                            'Первичная отправка конфига'
                        )

                        # Логика формирования и выдачи конфига юзеру
                        ans_json = await (
                            get_data(
                                f"""
{os.getenv('SET_PEER')}/{callback.from_user.username}+{callback.message.chat.id}
"""
                            )
                        )
                        file = await get_file_from_data(
                            callback.from_user.username, ans_json
                        )
                        await callback.message.answer_document(
                            FSInputFile(path=f"configs/{file}.conf")
                        )
                        await state.update_data(new_buy_state=1)
                        await state.update_data(buy_type="0")
                        await asyncio.sleep(config.SLEEP_TIME)
                        await msg1.delete()
                        await msg2.delete()

                    else:
                        await bot.send_message(
                            callback.message.chat.id,
                            'Ищите конфиг выше :^)'
                        )
            elif buy_type == '2':
                perm_state = await state.get_data()
                payment_status = data.get('new_buy_state')

                if payment_info.paid:
                    if payment_status == 0:

                        # логика продления выбранного конфига
                        ans_json = await (
                            get_data(
                                f"""
{config.EXTEND_PEER}/{config_name.split('-')[0]}
"""
                            )
                        )

                        if ans_json['Message'].startswith(
                            '1 Month added successfully'
                        ):

                            await callback.message.delete()

                            msg2 = await bot.send_message(
                                callback.message.chat.id,
                                'Туннель успешно продлен!'
                            )

                            await asyncio.sleep(config.SLEEP_TIME)
                            await msg1.delete()
                            await msg2.delete()

                        else:
                            await bot.send_message(
                                callback.message.chat.id,
                                'Если Вы видите данное ообщение, \
                                сообщите администратору :/'
                            )
                        await state.update_data(buy_type="0")
                        await state.update_data(new_buy_state=1)

                    else:
                        await bot.send_message(
                            callback.message.chat.id, 'Ищите инфу выше :^)'
                        )

        elif payment_info.status in ["pending", "waiting_for_capture"]:
            await bot.send_message(
                callback.message.chat.id,
                "Платеж еще обрабатывается, пожалуйста, \
                    подождите несколько секунд."
            )
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=str(payment_info.status)
            )
        else:
            await bot.send_message(
                callback.message.chat.id,
                f"""
                Платеж не был успешным. Статус: {payment_info.status}. \
                Обратитесь в поддержку.
                """
            )

    except Exception as e:
        logging.error(f"Ошибка при проверке платежа: {e}")
        await bot.send_message(
            callback.message.chat.id,
            "Произошла ошибка при проверке платежа. Попробуйте позже."
        )


# echo bot
@dp.message(F.text)
async def echo(message: Message):
    sent_message = await message.answer(message.text)
    await message.delete()
    await asyncio.sleep(10)
    await sent_message.delete()


async def main():
    await dp.start_polling(bot)
    await set_commands()


if __name__ == "__main__":

    # logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{config.BASE_DIR}/logs/main.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Бот запущен. Струячим.")

    asyncio.run(main())
