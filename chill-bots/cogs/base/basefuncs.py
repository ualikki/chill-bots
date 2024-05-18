import disnake


async def punish_logs(emb):
    from aiohttp import ClientSession
    async with ClientSession() as session:
        await disnake.Webhook.from_url('https://discord.com/api/webhooks/1074217429368066079/'
                                       'bN61Zy6GxOZSIPzMevmdEz9Hy1DM-zbxw9KpdreNLK6Yq1ZW8hFK6kcMRmXSu9rEbDW2',
                                       session=session).send(embed=emb)
