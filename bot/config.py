import os

from aiogram import types
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PAYMENTS_TOKEN = os.getenv('PAYMASTER_TOKEN')
CONTACT = os.getenv('CONTACT')
CONTACT_CHANELL = os.getenv('CONTACT_CHANELL')
PRICE = int(os.getenv('PRICE'))
PRICE_LABELED = types.LabeledPrice(
    label="Подписка на 1 месяц", amount=PRICE * 100
)
URL = os.getenv('URL')
URL2 = os.getenv('URL2')
URL3 = os.getenv('URL3')
YOKASSA_API_KEY = os.getenv('YOKASSA_API_KEY')
MARKET_ID = os.getenv('MARKET_ID')
GET_PEER_LIST = os.getenv('GET_PEER_LIST')
SET_PEER = os.getenv('SET_PEER')
EXTEND_PEER = os.getenv('EXTEND_PEER')
SLEEP_TIME = int(os.getenv('SLEEP_TIME'))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, 'photos')
ADMIN_ID_1 = os.getenv('ADMIN_ID_1')
ADMIN_ID_2 = os.getenv('ADMIN_ID_2')
