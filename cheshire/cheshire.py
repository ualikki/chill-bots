from disnake.ext import commands
from config import keys
from os import listdir

import disnake

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all(),
                   test_guilds=[971007825218240532, 983432883714789476, 1247575810131492886])

for name in listdir('cogs'):
    if name.endswith('.py'):
        bot.load_extension(f'cogs.{name[:-3]}')

bot.run(keys["cheshire"])
