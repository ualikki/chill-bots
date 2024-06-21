from config import keys
from functools import wraps

import disnake
import psycopg2


async def send_logs(emb):  # В ближайшее время эта штука будет предназначаться для всех логов
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


def create_user(user: disnake.Member):  # Здесь мы добавляем аккаунт пользователя в БД
    con = connect()
    cur = con.cursor()
    a = True
    cur.execute(f"SELECT uid FROM users WHERE uid = {user.id} AND guild = {user.guild.id}")
    account = cur.fetchone()
    if account:  # Проверяем, существует ли такой аккаунт
        a = False  # Если да, ничего не делаем
    else:
        cur.execute(f"INSERT INTO users(uid, guild) VALUES ({user.id}, {user.guild.id})")
        con.commit()  # Если нет, создаём новый
    con.close()
    return a  # И говорим, был ли создан новый аккаунт


def create_guild(guild: disnake.Guild):
    con = connect()
    cur = con.cursor()
    cur.execute(f"SELECT id FROM guilds WHERE id = {guild.id}")
    gld = cur.fetchone()
    if not gld:  # Проверяем, существует ли такой сервер
        cur.execute(f"INSERT INTO guilds(id) VALUES ({guild.id})")
        con.commit()  # Если нет, создаём новый
    con.close()


def update_users(user: disnake.Member, **qwargs):
    con = connect()
    cur = con.cursor()
    for i in qwargs:
        cur.execute(f"UPDATE users SET {i} = {i} + {qwargs[i]} WHERE uid = {user.id}")
        con.commit()
    con.close()


def update_guilds(guild: disnake.Guild, **qwargs):
    con = connect()
    cur = con.cursor()
    for i in qwargs:
        cur.execute(f"UPDATE guilds SET {i} = {qwargs[i]} WHERE id = {guild.id}")
        con.commit()
    con.close()


def update_market(name, **qwargs):
    con = connect()
    cur = con.cursor()
    for i in qwargs:
        cur.execute(f"UPDATE market SET {i} = {qwargs[i]} WHERE name = {name}")
        con.commit()
    con.close()


def get_from_db(table, column, value, *args):
    con = connect()
    cur = con.cursor()
    if isinstance(value, str):
        value = "'" + value + "'"
    if column is None:
        value = column = 1
    cur.execute(f"SELECT {', '.join(args)} FROM {table} WHERE {column} = {value}")
    values = cur.fetchall()
    con.close()
    return values


def update_logs(func):
    @wraps(func)
    async def wrapper(*args, **qwargs):
        con = connect()
        cur = con.cursor()
        for i in qwargs:
            if i not in ('self', 'inter') and qwargs[i]:
                cur.execute(f"UPDATE guilds SET {i}_logs = {qwargs[i].id} WHERE id = {qwargs['inter'].guild.id}")
                con.commit()
        con.close()
        await func(*args, **qwargs)
    return wrapper
