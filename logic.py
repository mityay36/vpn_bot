import aiohttp


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
                data = await response.text()
                return data
            else:
                return f"Error: {response.status}"


async def post_data(url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return f"Error: {response.status}"
