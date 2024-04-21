import disnake
from disnake.ext import commands
import requests
from config import keys


bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all(),
                   test_guilds=[983432883714789476])


@bot.event
async def on_member_join(member: disnake.Member):
    emb = disnake.Embed(title='Добро пожаловать!', description=f'{member.name}, рады видеть вас на сервере!')
    emb.set_footer(text=f'Теперь нас {member.guild.member_count}')
    await bot.get_channel(983432883714789479).send(embed=emb)


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
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
    else:
        await inter.guild.get_channel(1209893365483573318).send(str(error))
        raise error

bot.run(keys["cheshire"])
