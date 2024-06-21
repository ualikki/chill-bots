from disnake.ext import commands
from basefuncs import send_logs
from disnake import Embed


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = Embed()
        send_logs(log_channel, embed)

    ...


def setup(bot):
    bot.add_cog(Logs(bot))
