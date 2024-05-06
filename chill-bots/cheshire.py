import disnake
from disnake.ext import commands
import requests
from config import keys

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=disnake.Intents.all(),
                   test_guilds=[983432883714789476, 971007825218240532])


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


@bot.slash_command()
@commands.default_member_permissions(administrator=True)
async def kick(inter, user: disnake.Member):
    await user.kick()


@bot.slash_command()
@commands.default_member_permissions(administrator=True)
async def mute(inter, user: disnake.Member, hours: int = 0, minutes: int = 0, seconds: int = 0):
    await user.timeout(duration=hours * 3600 + minutes * 60 + seconds)


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
    else:
        print(error)
        await inter.guild.get_channel(1209893365483573318).send(str(error))
        raise error


bot.run(keys["cheshire"])
