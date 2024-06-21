from disnake.ext import commands
from random import randint
from asyncio import sleep
from datetime import datetime
from basefuncs import punish_logs, create_user, update_users, create_guild, get_from_db

'''Важное замечание: при попытке запустить данный файл эта строка вернёт ошибку, поскольку файл находится на уровень
выше, и следует писать ..basefuncs. Однако при загрузке файла через disnake.Bot.load_extension он выполняется как часть
основного файла, соответственно, импорты выполняются относительно cheshire.py'''

import disnake


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.c = 0

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if create_user(member):  # Приветствуем только пользователей, зашедших впервые
            emb = disnake.Embed(title='Добро пожаловать!', description=f'{member.name}, рады видеть вас на сервере!')
            emb.set_footer(text=f'Теперь нас {member.guild.member_count}')
            await self.bot.get_channel(983432883714789479).send(embed=emb)

    @commands.Cog.listener()
    async def on_ready(self):
        await sleep(2)  # Необходимо, чтобы информация успевала подгружаться
        for guild in self.bot.guilds:
            create_guild(guild)
            for user in guild.members:
                create_user(user)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        self.c += 1
        if not message.author.bot:
            update_users(message.author, money=randint(
                *(get_from_db('guilds', 'id', message.guild.id, 'min_payment', 'max_payment')[0])))
        if not self.c % 5:
            await self.update_color_roles()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: disnake.Reaction, user):
        if reaction.emoji == '🚫':
            if reaction.count >= 5:
                msg = reaction.message
                if msg.author.guild_permissions.administrator or msg.author.bot:
                    return
                emb = disnake.Embed(title='Сообщение заблокировано')
                emb.add_field('Содержимое:', msg.content)
                emb.add_field('Автор:', msg.author)
                emb.add_field('Сообщение удалено:',
                              '\n'.join(str(i) for i in await reaction.users().flatten()))
                await punish_logs(emb=emb)
                await msg.delete()

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
        else:
            await inter.response.send_message('При выполнении команды произошла ошибка. Вы можете написать разработчику'
                                              ' (<@817312010000924732>), при этом желательно указать время и'
                                              ' обстоятельства, при которых произошла ошибка (название команды и '
                                              'использованные аргументы)', ephemeral=True)
            print(error)
            with open('logs.txt', 'a', encoding='utf-8') as f:
                f.write(f'\n{str(datetime.now())}\n{str(error)}\n{str(inter.data)}\n')

    async def update_color_roles(self):
        pass


def setup(bot):
    bot.add_cog(Events(bot))
