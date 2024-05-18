from cheshire.config import keys

import disnake
import psycopg2


async def punish_logs(emb):
    from aiohttp import ClientSession
    async with ClientSession() as session:
        await disnake.Webhook.from_url(keys['punish_hook'],
                                       session=session).send(embed=emb)


def connect():
    return psycopg2.connect(
        dbname=keys['database']['name'],
        user=keys['database']['user'],
        password=keys['database']['password'],
        host=keys['database']['host'],
        port=keys['database']['port'])


def create_user(user: disnake.Member):
    con = connect()
    a = True
    if ...:
        a = False
    else:
        ...
    con.close()
    return a
