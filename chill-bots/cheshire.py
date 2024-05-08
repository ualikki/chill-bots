import disnake
from disnake.ext import commands
import requests
from config import keys
from aiohttp import ClientSession
from random import randint

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all(),
                   test_guilds=[983432883714789476, 971007825218240532])
c = 0


@bot.event
async def on_member_join(member: disnake.Member):
    emb = disnake.Embed(title='Добро пожаловать!', description=f'{member.name}, рады видеть вас на сервере!')
    emb.set_footer(text=f'Теперь нас {member.guild.member_count}')
    await bot.get_channel(983432883714789479).send(embed=emb)


@bot.event
async def on_message(message):
    global c
    c += 1
    if not c % 5:
        colorrole = bot.get_guild(983432883714789476).get_role(1237743816836907141)
        await colorrole.edit(color=randint(1, 16777216))


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


@bot.slash_command()
@commands.default_member_permissions(administrator=True)
async def ban(inter, user: disnake.Member, reason: str):
    await user.send(
        embed=disnake.Embed(title='Уведомление',
                            description=f'Вас были заблокированы на сервере Чиллвилль администратором {inter.author} '
                                        f'по причине "{reason}". Вы можете подать аппеляцию, если не согласны с '
                                        f'наказанием. Для этого необходимо заполнить форму: '
                                        f'https://forms.gle/SDfNdS4R5cDE9VN7A'))
    await user.ban()
    emb = disnake.Embed(title='БАН')
    emb.add_field('Нарушитель', str(user))
    emb.add_field('Администратор', str(inter.author))
    emb.add_field('Причина', reason)
    await punish_logs(emb)


@bot.slash_command()
@commands.default_member_permissions(administrator=True)
async def kick(inter, user: disnake.Member, reason: str):
    await user.kick()
    emb = disnake.Embed(title='Кик')
    emb.add_field('Нарушитель', str(user))
    emb.add_field('Администратор', str(inter.author))
    emb.add_field('Причина', reason)
    await punish_logs(emb)


@bot.slash_command()
@commands.default_member_permissions(administrator=True)
async def mute(inter, user: disnake.Member, reason: str, hours: int = 0, minutes: int = 0, seconds: int = 0):
    await user.timeout(duration=hours * 3600 + minutes * 60 + seconds)
    emb = disnake.Embed(title='Таймаут')
    emb.add_field('Нарушитель', str(user))
    emb.add_field('Администратор', str(inter.author))
    emb.add_field('Причина', reason)
    await punish_logs(emb)


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
    else:
        await inter.guild.get_channel(1209893365483573318).send(str(error))
        raise error


async def punish_logs(emb):
    async with ClientSession() as session:
        await disnake.Webhook.from_url('https://discord.com/api/webhooks/1074217429368066079/'
                                       'bN61Zy6GxOZSIPzMevmdEz9Hy1DM-zbxw9KpdreNLK6Yq1ZW8hFK6kcMRmXSu9rEbDW2',
                                       session=session).send(embed=emb)


bot.run(keys["cheshire"])
