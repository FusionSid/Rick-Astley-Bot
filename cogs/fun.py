import json
import datetime

import discord
from discord.ext import commands
from discord.commands import slash_command


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=500)

    @discord.ui.button(style=discord.ButtonStyle.green, label="Claim", custom_id="b1")
    async def button1(self, button, interaction):
        button.style = discord.ButtonStyle.red
        button.label = "Claimed"
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("https://imgur.com/NQinKJB", ephemeral=True)
        with open("./database/count.json") as f:
            data = json.load(f)
        data["claimrickroll"] += 1
        count = data["claimrickroll"]
        await interaction.followup.send(
            f"You were the {count} person to get rick rolled", ephemeral=True
        )
        with open("./database/count.json", "w") as f:
            json.dump(data, f, indent=4)


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def claim(self, ctx):
        em = discord.Embed(title="Claim 100k Coins", color=discord.Color.random())
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em, view=MyView())


    @slash_command(name="claim", description="Claim you coins")
    async def _claim(self, ctx):
        em = discord.Embed(title="Claim 100k Coins", color=discord.Color.random())
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em, view=MyView())


def setup(client):
    client.add_cog(Fun(client))
