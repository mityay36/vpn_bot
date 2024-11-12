import os
from aiogram import types

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENTS_TOKEN = os.getenv('PAYMASTER_TOKEN')
CONTACT = os.getenv('CONTACT')
PRICE = int(os.getenv('PRICE'))
PRICE_LABELED = types.LabeledPrice(
    label="Подписка на 1 месяц", amount=PRICE*100
)
URL = os.getenv('URL')
YOKASSA_API_KEY = os.getenv('YOKASSA_API_KEY')
MARKET_ID = os.getenv('MARKET_ID')
GET_PEER_LIST = os.getenv('GET_PEER_LIST')
SET_PEER = os.getenv('SET_PEER')
EXTEND_PEER = os.getenv('EXTEND_PEER')