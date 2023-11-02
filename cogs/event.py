import json
import random

import discord
from discord.ext import commands


class Event(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if (
            self.client.user.mentioned_in(message)
            and message.mention_everyone is False
            and message.reference is None
        ):
            with open("./database/lyrics.json") as f:
                data = json.load(f)

            send = random.choice(data)
            await message.channel.send(send)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online")


def setup(client):
    client.add_cog(Event(client))
