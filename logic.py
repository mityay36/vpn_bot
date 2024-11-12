import asyncio
import json
import uuid
from datetime import datetime

import aiofiles
import aiohttp
from yookassa import Payment

import config


def get_payment():
    return Payment.create({
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


def get_tunnel_list(chat_id: int):
    tunnel_list = [
        ('urmomgay_wg0', 'alive'),
        ('vasya1_wg0', 'dead'),
        ('remotecontrol_of_america_wg0', 'dead'),
        ('num1', 'dead'),
        ('num2', 'dead'),
        ('nu3', 'dead')
    ]
    # вообще тут должно быть async & await через io request
    return tunnel_list


async def get_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                await session.close()
                return data
            else:
                await session.close()
                return f"Error: {response.status}"


async def post_data(url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                await session.close()
                return data
            else:
                await session.close()
                return f"Error: {response.status}"


async def get_file_from_data(user, cfg_json):
    cfg = f'''[Interface]
PrivateKey = {cfg_json['Interface']['PrivateKey']}
Address = {cfg_json['Interface']['Address']}
DNS = {cfg_json['Interface']['DNS']}
MTU = {cfg_json['Interface']['MTU']}

[Peer]
PublicKey = {cfg_json['Peer']['PublicKey']}
AllowedIPs = {cfg_json['Peer']['AllowedIPs']}
Endpoint = {cfg_json['Peer']['Endpoint']}
PersistentKeepalive = {cfg_json['Peer']['PersistentKeepalive']}
'''
    # current_date = datetime.now()
    # date_str = current_date.strftime("%Y-%m-%d-%H-%M-%S")
    # filename = f'{user}-{date_str}'
    filename = cfg_json['FileName']
    async with aiofiles.open(f'configs/{filename}.conf', mode='w') as file:
        await file.write(f"{cfg}")

    return filename
