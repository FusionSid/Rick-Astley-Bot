import datetime

import discord
import aiohttp
from discord.ext import commands


class CodeInput(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code = None

        self.add_item(discord.ui.InputText(label="Please enter the code", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        self.code = self.children[0].value
        return await interaction.response.send_message(
            "Running code now...", ephemeral=True
        )


class Ricklang(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ricklang(self, ctx):
        modal = CodeInput(title="Code Input")
        await ctx.send_modal(modal)
        await modal.wait()

        if modal.code is None:
            return await ctx.respond("Invalid Input", ephemeral=True)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.fusionsid.xyz/api/runcode",
                json={"code": modal.code, "language": "rickroll_lang"},
            ) as resp:
                response = await resp.json()
            if resp.status != 200:
                em = discord.Embed(
                    title="Rickroll-Lang",
                    description="Something went wrong!\n(API probably had a skill issue)",
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now(),
                )
                await ctx.respond(embed=em)

        em = discord.Embed(
            title="Output",
            color=discord.Color.blue(),
            description=f"""```\n{response['stdout']}\n```""",
            timestamp=datetime.datetime.now(),
        )

        await ctx.respond(embed=em)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):

            async def better_time(cd: int):
                time = f"{cd}s"
                if cd > 60:
                    minutes = cd - (cd % 60)
                    seconds = cd - minutes
                    minutes = int(minutes / 60)
                    time = f"{minutes}min {seconds}s"
                    if minutes > 60:
                        hoursglad = minutes - (minutes % 60)
                        hours = int(hoursglad / 60)
                        minutes = minutes - (hours * 60)
                        time = f"{hours}h {minutes}min {seconds}s"
                return time

            cd = round(error.retry_after)
            if cd == 0:
                cd = 1
            retry_after = await better_time(cd)
            em = discord.Embed(
                title="Wow buddy, Slow it down\nThis command is on cooldown",
                description=f"Try again in **{retry_after}**",
                color=discord.Color.red(),
            )
            em.timestamp = datetime.datetime.utcnow()
            error_msg = await ctx.send(embed=em)

            await ctx.message.add_reaction("⚠️")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):

            async def better_time(cd: int):
                time = f"{cd}s"
                if cd > 60:
                    minutes = cd - (cd % 60)
                    seconds = cd - minutes
                    minutes = int(minutes / 60)
                    time = f"{minutes}min {seconds}s"
                    if minutes > 60:
                        hoursglad = minutes - (minutes % 60)
                        hours = int(hoursglad / 60)
                        minutes = minutes - (hours * 60)
                        time = f"{hours}h {minutes}min {seconds}s"
                return time

            cd = round(error.retry_after)
            if cd == 0:
                cd = 1
            retry_after = await better_time(cd)
            em = discord.Embed(
                title="Wow buddy, Slow it down\nThis command is on cooldown",
                description=f"Try again in **{retry_after}**",
                color=discord.Color.red(),
            )
            em.timestamp = datetime.datetime.utcnow()
            error_msg = await ctx.send(embed=em)

            await ctx.message.add_reaction("⚠️")


def setup(client):
    client.add_cog(Ricklang(client))
