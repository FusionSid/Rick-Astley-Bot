import os

from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

client = commands.Bot(">")

for i in os.listdir("cogs/"):
    client.load_extension(f"cogs.{i.rstrip('.py')}")


client.run(os.environ["TOKEN"])