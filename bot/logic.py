import uuid

import aiofiles
import aiohttp
import config
from yookassa import Payment


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
    filename = cfg_json['FileName']
    async with aiofiles.open(f'configs/{filename}.conf', mode='w') as file:
        await file.write(f"{cfg}")

    return filename


async def get_tunnel_list(username):
    tunnels = await get_data(f'{config.GET_PEER_LIST}/{username}')

    if 'Error' in tunnels:
        return False

    out = []
    for tunnel in tunnels:
        if tunnel['Status'] == 'Paid':
            status = '🟢'
        else:
            status = '🔴'
        out.append((tunnel['Name'], status))

    return out
