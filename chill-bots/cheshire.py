import disnake
from disnake.ext import commands
import sqlite3
import random
import requests
import economy
from config import keys

# Подключение к базе данных SQLite3
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

# Создание таблицы для хранения данных пользователя
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        num INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL
    )
''')
conn.commit()
conn.close()
CANT_EARN = [1109470825062600835, 1054826803602149447, 1198684792414277743, 1132598948201238558, 983610204975407114]

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all(),
                   test_guilds=[983432883714789476])
TARGET_ROLE_NAME = "Постоялец"


@bot.event
async def on_ready():
    all_members = bot.get_all_members()

    for member in all_members:
        economy.create_user(member.id)


@bot.slash_command()
async def balance(inter, user: disnake.Member | None = None):
    if not user:
        user = inter.author

    balance = economy.balance(user.id)

    if balance is None:
        economy.create_user(user.id)
    await inter.response.send_message(f'Баланс {user.name}: {balance if balance else 0} монет')


@bot.slash_command()
@commands.cooldown(1, 3600, commands.BucketType.user)
async def earn(inter):
    user_id = inter.author.id

    earned_money = random.randint(70, 120)

    economy.add(user_id, earned_money)

    await inter.response.send_message(f'Вы заработали {earned_money} монет!')


@bot.slash_command()
async def fire(inter, amount: int):
    user_id = inter.author.id

    balance = economy.balance(user_id)
    if not balance or balance < amount or amount <= 0:
        await inter.response.send_message('У вас недостаточно денег для этой операции.')
        return

    target_role = disnake.utils.get(inter.guild.roles, name="Постоялец")
    members_with_role = [member for member in inter.guild.members if target_role in member.roles]

    recipients = random.sample(members_with_role, min(5, len(members_with_role)))

    share = amount // len(recipients)
    for recipient in recipients:
        economy.send(user_id, recipient.id, share)

    await inter.response.send_message(
        f'{amount} монет распределено между {len(recipients)} участниками с ролью "{target_role.name}"'
        f':\n{", ".join([recipient.name for recipient in recipients])}.')


@bot.slash_command()
async def url(inter, link: str):
    res = requests.post('https://api.short.io/links', json={
        'domain': 'go.trelesco.xyz',
        'originalURL': link,
    }, headers={
        'authorization': 'sk_mW8USxsNUrAvJRwz',
        'content-type': 'application/json'
    }, )

    res.raise_for_status()
    shortlink = res.json()['shortURL']
    await inter.response.send_message(shortlink)


@bot.event
async def on_member_join(member):
    economy.create_user(member.id)


@bot.event
async def on_message(message):
    if message.channel.id not in CANT_EARN:
        user_id = message.author.id
        amount = random.randint(1, 5)
        economy.add(user_id, amount)


@bot.slash_command()
async def buy_ticket(inter):
    user_id = inter.author.id
    balance = economy.balance(user_id)

    if not balance or balance < 2000:
        await inter.response.send_message('Для покупки билета вам нужно 1000 монет!')
    else:
        economy.send(user_id, 1, 2000)
        economy.create_ticket(user_id)

        await inter.response.send_message(
            "Вы купили 1 лотерейный билет. Просмотреть ваши билеты можно с помощью команды /tickets")


@bot.slash_command()
async def tickets(inter):
    user_id = inter.author.id
    tickets = economy.get_tickets(user_id)

    await inter.response.send_message(f"Ваши билеты:\n{', '.join([str(ticket[0]) for ticket in tickets])}")


@bot.slash_command()
async def sql(inter, query: str):
    if inter.author.id == 1038379463127347210:
        conn = sqlite3.connect('economy.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        await inter.response.send_message("Выполнено")
    else:
        await inter.response.send_message("Отказано в доступе!")


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
    else:
        await inter.guild.get_channel(1209893365483573318).send(str(error))
        raise error


@bot.slash_command()
@commands.has_permissions(administrator=True)
async def lottery(inter):
    tickets = economy.get_tickets()
    win_ticket = random.randint(1, len(tickets))
    winner = economy.get_ticket(win_ticket)
    user = bot.get_user(winner)
    await inter.response.send_message(f"Выигрышный билет - билет №{win_ticket}\n\nПобедитель - {user.mention}")


@bot.slash_command()
async def send(inter, recipient: disnake.Member, amount: int):
    if economy.balance(inter.author.id) >= amount > 0:
        economy.send(inter.author.id, recipient.id, amount)
        await inter.response.send_message(f"Отправлено {amount} для <@{recipient.id}>")
    else:
        await inter.response.send_message("Проблема с количеством...")


@bot.slash_command()
async def statistic(inter):
    stats = economy.get_stats()
    emb = disnake.Embed(title='Статистика')
    emb.add_field('Общая денежная масса', str(stats[0]))
    emb.add_field('Бюджет Чиллвилля', str(stats[1][1]), inline=False)
    emb.add_field('Денег в ходу', str(stats[0] - stats[1][1]))
    emb.add_field('Топ-10 пользователей', '\n'.join(f'<@{i[0]}>: {i[1]}' for i in stats[2]), inline=False)
    await inter.response.send_message(embed=emb)


@bot.slash_command()
@commands.cooldown(5, 3600, commands.BucketType.user)
async def russian_roulette(inter, bet: int, bullets: int = 1):
    if not 0 < bullets < 7:
        await inter.response.send_message('Револьвер шестизарядный')
        return
    if economy.balance(inter.author.id) >= bet > 0:
        economy.send(inter.author.id, 2, bet)
    else:
        await inter.response.send_message('С деньгами всегда так: или их не хватает, или вы не хотите их отдавать')
        return
    if random.randint(1, 6) > bullets:
        economy.send(2, inter.author.id, bet * bullets // 3 + bet)
        await inter.response.send_message(f'Поздравляю, вы выиграли {bet + bet * bullets // 3}')
    else:
        await inter.author.timeout(duration=(dur := (random.randint(5, 15) - bullets)) * 60)
        await inter.response.send_message(f'Очень жаль, но вы проиграли. Врачи спасут вашу жизнь,'
                                          f' но им потребуется {dur} минут')


@bot.slash_command()
async def dice(inter, bet: int, number: int = 0, minimum: int = 1, maximum: int = 6):
    if number and (minimum != 6 or maximum != 1):
        await inter.response.send_message('Можно ставить на число или на диапазон')
        return
    if minimum < 1 or maximum > 6 or maximum - minimum < 0 or maximum < 1 or minimum > 6:
        await inter.response.send_message('Вы, вероятно, не вполне знакомы с игральной костью. Я раскрою вам одну '
                                          'древнюю тайну: у кубика шесть граней, от одного до шести')
    if economy.balance(inter.author.id) >= bet > 0:
        economy.send(inter.author.id, 2, bet)
        rolled_number = random.randint(1, 6)
        if number:
            minimum = maximum = number
        if minimum <= rolled_number <= maximum:
            economy.send(2, inter.author.id, bet * 6 // (maximum - minimum + 1))
            await inter.response.send_message(f'Поздравляю, вы выиграли {bet * 6 // (maximum - minimum + 1)}')
            return
        else:
            await inter.response.send_message('К сожалению, вы не угадали')
            return
    else:
        await inter.response.send_message('С деньгами всегда так: или их не хватает, или вы не хотите их отдавать')

bot.run(keys["cheshire"])
