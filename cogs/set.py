import json

import discord
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def setprefix(self, ctx, prefix:str):
        with open("database/config.json") as f:
            data = json.load(f)

        data["prefix"] = prefix

        with open("database/config.json", 'w') as f:
            json.dump(data, f, indent=4)


def setup(client):
    client.add_cog(Settings(client))