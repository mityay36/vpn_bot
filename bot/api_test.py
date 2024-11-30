import asyncio

import bot.config as config
from bot.logic import get_data


async def get_tunnel_list(username: str):
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

    return print(out)


# Configuration.account_id = str(config.MARKET_ID)
# Configuration.secret_key = str(config.YOKASSA_API_KEY)
# Configuration.configure(config.MARKET_ID, config.YOKASSA_API_KEY)

# payment = Payment.create({
#         "amount": {
#             "value": '100'+'.00',
#             "currency": "RUB"
#         },
#         "payment_method_data": {
#             "type": "sberbank",
#         },
#         "confirmation": {
#             "type": "redirect",
#             "return_url": "https://t.me/vpnachos_bot"
#         },
#         "description": "Заказ №72"
#     }, str(uuid.uuid4()))

# payment_data = json.loads(payment.json())
# print(payment_data)
# payment_id = payment_data['id']
# payment_url = (payment_data['confirmation'])['confirmation_url']


# payment_info = Payment.find_one('')
# print(json.loads(payment_info.json()))
ans_json = asyncio.run((get_data(f"{config.EXTEND_PEER}/15")))
print(ans_json["Message"])
