from disnake.ext import commands


class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.default_member_permissions(administrator=True)
    async def write(self, inter, message):
        await inter.channel.send(message)

    @commands.Cog.listener()
    async def url(self, inter, link: str):
        import requests
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


def setup(bot):
    bot.add_cog(Other(bot))
