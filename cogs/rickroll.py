import json
import datetime

import discord
import aiohttp
from discord.ext import commands


class RickrollLangCodeInput(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.request_data = None

        self.add_item(
            discord.ui.InputText(
                label="Source Code:",
                placeholder="The code that will be run",
                style=discord.InputTextStyle.paragraph,
                required=True,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Standard Input:",
                placeholder="Will be provided as input",
                style=discord.InputTextStyle.short,
                required=False,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Enviroment Variables (Seperate by new line):",
                placeholder="Add each variable in the format:\n<KEY>=<VALUE>\nExamples:\nName=Simplex\nAge=2",
                style=discord.InputTextStyle.paragraph,
                required=False,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Processing input...", ephemeral=True)

        code = self.children[0].value
        stdin = self.children[1].value
        envs = self.children[2].value

        if code is None or stdin is None or envs is None:
            return

        self.request_data = {"code": code, "language": "ricklang", "input": stdin}

        if not envs:
            return

        try:
            envs = dict(map(lambda line: line.split("=", 1), envs.split("\n")))
        except ValueError:
            return

        self.request_data = {**self.request_data, "enviromentVariables": envs}


class Ricklang(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ricklang(
        self,
        ctx: discord.ApplicationContext,
        use_cache: discord.Option(
            bool,
            "If set to true the API will check the cache if this code was run before and if yes use that instead",  # noqa
            default=True,
        ),  # type: ignore
    ):
        modal = RickrollLangCodeInput(title="Code Input")
        await ctx.send_modal(modal)

        await modal.wait()  # wait for the modal to complete

        if modal.request_data is None:
            return await ctx.respond(
                embed=discord.Embed(
                    title="Invalid Input!",
                    description="Invalid input was provided to the modal",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://rce.fusionsid.com/runcode",
                json={
                    **modal.request_data,
                    "use_cache": use_cache,
                },
            ) as resp:
                try:
                    resp.raise_for_status()
                except aiohttp.ClientResponseError:
                    return await ctx.respond(
                        embed=discord.Embed(
                            title="Rickroll-Lang",
                            description="Something went wrong while making the request!",
                            color=discord.Color.red(),
                        )
                    )

                try:
                    parsed = await resp.json()
                    if parsed["success"] is False:
                        raise TypeError

                    data = parsed["data"]
                except (
                    aiohttp.ContentTypeError,
                    json.JSONDecodeError,
                    TypeError,
                ):
                    return await ctx.respond(
                        embed=discord.Embed(
                            title="Rickroll-Lang",
                            description="Something went wrong while decoding the request! (Probably API skill issue)",
                            color=discord.Color.red(),
                        )
                    )

        em = discord.Embed(
            title="Output",
            color=discord.Color.blue(),
            description=f"""```\n{data['stdout']}\n```""",
        )

        if data["timedOut"]:
            em.add_field(
                name="Timed Out",
                value="The code your provided took too long to run",
                inline=True,
            )
            return await ctx.respond(embed=em)

        if data["outOfMemory"]:
            em.add_field(
                name="Memory Error",
                value="The code your provided used up all the memory",
                inline=True,
            )

        em.add_field(
            name="Execution Time", value=f"{data['executionTime']}ms", inline=True
        )

        if stderr := data["stderr"]:
            em.add_field(name="stderr", value=stderr)

        return await ctx.respond(embed=em)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if not isinstance(error, commands.CommandOnCooldown):
            return

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
                    minutes -= hours * 60
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

        em.timestamp = datetime.datetime.now(datetime.timezone.utc)
        await ctx.respond(embed=em)


def setup(client):
    client.add_cog(Ricklang(client))
