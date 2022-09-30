import json
import datetime

import aiohttp
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

    @slash_command(name="claim", description="Claim you coins")
    async def _claim(self, ctx):
        em = discord.Embed(title="Claim 100k Coins", color=discord.Color.random())
        em.timestamp = datetime.datetime.utcnow()
        await ctx.respond(embed=em, view=MyView())


    @commands.command(
        name="runcode",
        usage="runcode [language] [code]",
        description="Runs code",
        help="This command is used to run code. It supports many languages.",
    )
    async def runcode_(self, ctx, lang: str, *, code):
        code = code.replace("`", "")
        data = {"language": lang, "source": f"""{code}"""}
        url = "https://emkc.org/api/v1/piston/execute"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                try:
                    data = await resp.json()
                except Exception as e:
                    print(e)
                    data = resp
        if data["ran"] == True:
            em = discord.Embed(
                title="Code Output",
                description=f"```{data['output']}```",
                color=ctx.author.color,
            )
            await ctx.send(embed=em)
        if data["stderr"] != "":
            em = discord.Embed(
                title="Error!",
                description=f"```{data['stderr']}```",
                color=ctx.author.color,
            )
            await ctx.send(embed=em)


def setup(client):
    client.add_cog(Fun(client))
