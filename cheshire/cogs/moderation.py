from disnake.ext import commands
from basefuncs import punish_logs  # См. events

import disnake


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def ban(self, inter, user: disnake.Member, reason: str):
        await user.send(
            embed=disnake.Embed(title='Уведомление',
                                description=f'Вас были заблокированы на сервере {inter.guild.name} администратором'
                                            f' {inter.author} по причине "{reason}". Вы можете подать аппеляцию, если '
                                            f'не согласны с наказанием. Для этого необходимо заполнить форму: '
                                            f'https://forms.gle/SDfNdS4R5cDE9VN7A'))
        await user.ban()
        emb = disnake.Embed(title='БАН')
        emb.add_field('Нарушитель', str(user))
        emb.add_field('Администратор', str(inter.author))
        emb.add_field('Причина', reason)
        await punish_logs(emb)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def kick(self, inter, user: disnake.Member, reason: str):
        await user.kick()
        emb = disnake.Embed(title='Кик')
        emb.add_field('Нарушитель', str(user))
        emb.add_field('Администратор', str(inter.author))
        emb.add_field('Причина', reason)
        await punish_logs(emb)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def mute(self, inter, user: disnake.Member, reason: str, hours: int = 0, minutes: int = 0, seconds: int = 0):
        await user.timeout(duration=hours * 3600 + minutes * 60 + seconds)
        emb = disnake.Embed(title='Таймаут')
        emb.add_field('Нарушитель', str(user))
        emb.add_field('Администратор', str(inter.author))
        emb.add_field('Причина', reason)
        await punish_logs(emb)


def setup(bot):
    bot.add_cog(Moderation(bot))
