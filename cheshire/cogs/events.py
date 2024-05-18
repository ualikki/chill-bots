from disnake.ext import commands
from random import randint
from cheshire.basefuncs import punish_logs

import disnake


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.c = 0

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        emb = disnake.Embed(title='Добро пожаловать!', description=f'{member.name}, рады видеть вас на сервере!')
        emb.set_footer(text=f'Теперь нас {member.guild.member_count}')
        await self.bot.get_channel(983432883714789479).send(embed=emb)

    @commands.Cog.listener()
    async def on_message(self, message):
        self.c += 1
        if not self.c % 5:
            colorrole = self.bot.get_guild(983432883714789476).get_role(1237743816836907141)
            await colorrole.edit(color=randint(1, 16777216))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: disnake.Reaction, user):
        if reaction.emoji == '🚫':
            print(reaction.count)
            if reaction.count >= 5:
                msg = reaction.message
                emb = disnake.Embed(title='Сообщение заблокировано')
                emb.add_field('Содержимое:', msg.content)
                emb.add_field('Автор:', msg.author)
                emb.add_field('Сообщение удалено:',
                              '\n'.join(str(i) for i in await reaction.users().flatten()))
                await punish_logs(emb=emb)
                await msg.delete()

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CommandOnCooldown):
            await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
        else:
            await inter.guild.get_channel(1209893365483573318).send(str(error))
            raise error


def setup(bot):
    bot.add_cog(Events(bot))
