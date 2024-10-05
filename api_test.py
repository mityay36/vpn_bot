import json
import uuid

import requests
from yookassa import Payment, Configuration, Receipt

import config

Configuration.account_id = str(config.MARKET_ID)
Configuration.secret_key = str(config.YOKASSA_API_KEY)
Configuration.configure(config.MARKET_ID, config.YOKASSA_API_KEY)

payment = Payment.create({
        "amount": {
            "value": '100'+'.00',
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

payment_data = json.loads(payment.json())
print(payment_data)
payment_id = payment_data['id']
payment_url = (payment_data['confirmation'])['confirmation_url']
