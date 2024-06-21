from disnake.ext import commands
from basefuncs import update_guilds, update_logs  # См. events

import disnake


class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def set_color_role(self, inter, role: disnake.Role):
        update_guilds(inter.guild, color_role=role.id)
        await inter.response.send_message('Успешно', ephemeral=True)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def set_greeting_channel(self, inter, channel: disnake.TextChannel):
        update_guilds(inter.guild, greeting_channel=channel.id)
        await inter.response.send_message('Успешно', ephemeral=True)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def set_appeal_link(self, inter, text):
        update_guilds(inter.guild, appeal_link=text)
        await inter.response.send_message('Успешно', ephemeral=True)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    @update_logs
    async def set_logs(self, inter, users: disnake.TextChannel = None, messages: disnake.TextChannel = None,
                       moderation: disnake.TextChannel = None, voice: disnake.TextChannel = None,
                       channels: disnake.TextChannel = None, other: disnake.TextChannel = None):
        await inter.response.send_message('Успешно', ephemeral=True)


def setup(bot):
    bot.add_cog(Custom(bot))
