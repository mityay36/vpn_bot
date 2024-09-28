import os
from aiogram import types

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENTS_TOKEN = os.getenv('PAYMASTER_TOKEN')
CONTACT = os.getenv('CONTACT')
PRICE = int(os.getenv('PRICE'))
PRICE_LABELED = types.LabeledPrice(
    label="Подписка на 1 месяц", amount=200*100
)
URL = os.getenv('URL')
