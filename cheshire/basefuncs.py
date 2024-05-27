from config import keys

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
    print(user.id)
    con = connect()
    cur = con.cursor()
    a = True
    cur.execute(f"SELECT uid FROM users WHERE uid = {user.id}")
    account = cur.fetchone()
    if account:
        a = False
    else:
        cur.execute(f"INSERT INTO users(uid) VALUES ({user.id})")
        con.commit()
    con.close()
    return a


def update_money(user: disnake.Member, money):
    con = connect()
    cur = con.cursor()
    cur.execute(f"UPDATE users SET money = money + {money} WHERE uid = {user.id}")
    con.commit()
    con.close()
