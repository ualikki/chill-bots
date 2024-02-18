import disnake
from disnake.ext import commands
import sqlite3
import random
import asyncio
import economy
from config import keys

# Подключение к базе данных SQLite3
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all())

casino_id = 1198684792414277743

reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
blacks = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]

cursor.execute('''
    CREATE TABLE IF NOT EXISTS bets (
        roll_id INTEGER,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        num INTEGER,
        color TEXT
    )
''')
conn.commit()
conn.close()


@bot.event
async def on_ready():
    casino_channel = bot.get_channel(casino_id)
    with open("roll_id.txt") as file:
        roll = int(file.read())
    while True:
        await casino_channel.send("Новый запуск рулетки, результаты через 5 минут!\n\nЖду новых ставок!")
        await asyncio.sleep(300)
        result = random.randint(0, 36)
        color = ''
        if result in reds:
            color = "red"
        elif result in blacks:
            color = "black"
        bets = economy.get_bets(roll)
        roll += 1
        print(roll)
        with open("roll_id.txt", 'w') as file:
            file.write(str(roll))
        wins = f'На рулетке: {result} {color}!\n'
        for bet in bets:
            print(bet)
            if bet[3] == result:
                economy.send(2, bet[1], bet[2] * 36)
                wins += f"<@{bet[1]}> выиграл {bet[2]}\n"
            if bet[4] == color:
                economy.send(2, bet[1], bet[2] * 2)
                wins += f"<@{bet[1]}> выиграл {bet[2]}\n"
        await casino_channel.send(wins)


@bot.slash_command()
async def bet_roulette(inter, amount: int, number: int = None, color: str = None):
    if number is None and color is None:
        await inter.response.send_message("Вы должны сделать ставку!")
        return

    if number is not None and color is not None:
        await inter.response.send_message("Вы можете сделать ставку или на цвет или на число!")
        return

    if number is not None and (number < 0 or number > 36):
        await inter.response.send_message("Число должно быть в диапазоне [0, 36]!")
        return

    if color is not None and color not in ["red", "black", "красный", "черный", "чёрный"]:
        await inter.response.send_message("Выберите красный или чёрный!\n(red, black, красный, чёрный)")
        return

    with open("roll_id.txt") as file:
        roll_id = int(file.read())
    user_id = inter.author.id
    balance = economy.balance(user_id)

    if not balance or balance < amount or amount <= 0:
        await inter.response.send_message('У вас недостаточно денег.')
        return

    if color == "красный":
        color = "red"
    if color in ["черный", "чёрный"]:
        color = "black"

    economy.send(user_id, 2, amount)

    if color is not None:
        economy.bet_color(roll_id, user_id, amount, color)
    elif number is not None:
        economy.bet_number(roll_id, user_id, amount, number)
    else:
        await inter.response.send_message("Спасибо за донат!")
        return

    await inter.response.send_message("Ваша ставка записана!")


bot.run(keys["casino"])
