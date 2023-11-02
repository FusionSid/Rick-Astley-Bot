import os
import time
import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

__version__ = "0.0.1"


class RickAstley(commands.Bot):
    """
    The Rick Astley Class (subclass of: `discord.ext.commands.Bot`)
    """

    def __init__(self):
        self.cogs_list = []
        self.version = __version__
        self.last_login_time = datetime.datetime.now()

        intents = discord.Intents.all()
        allowed_mentions = discord.AllowedMentions(everyone=False)

        super().__init__(
            intents=intents,
            help_command=None,
            case_insensitive=True,
            command_prefix=">",
            owner_ids=[624076054969188363, 726987234284273675],
            allowed_mentions=allowed_mentions,
        )


def loading_bar(length: int, index: int, title: str, end: str):
    """
    Makes a loading bar when starting up the bot

    Parameters
        :param: length (int): The length of the list
        :param: index (int): Index of the list
        :param: title (str): The title of the loading bar
        :param: end (str): The message to say once the bar is done
    """
    percent_done = (index + 1) / length * 100
    done = round(percent_done / (100 / 50))
    togo = 50 - done

    done_str = "█" * int(done)
    togo_str = "░" * int(togo)

    print(f"{title} {done_str}{togo_str} {int(percent_done)}% Done", end="\r")

    if round(percent_done) == 100:
        print(f"\n\n{end}\n")


def start_bot(client: RickAstley):
    """
    Starts up the bot

    Parameters
        :param client (RickAstley): The amazing rick astley client
    """
    cogs = [
        f"cogs.{filename[:-3]}"
        for filename in os.listdir("cogs/")
        if filename.endswith(".py")
    ]
    print("\n")
    for index, cog in enumerate(cogs):
        client.cogs_list = cogs
        client.load_extension(cog)
        loading_bar(len(cogs), index, "Loading Cogs:", "Loaded All Cogs ✅")
        time.sleep(1)

    time.sleep(1)

    client.run(os.environ["TOKEN"])


if __name__ == "__main__":
    client = RickAstley()

    @client.event
    async def on_message(message):
        if message.author.bot:
            return

        await client.process_commands(message)

    start_bot(client)
