import datetime

import discord
from discord.ext import commands

import runner

class Ricklang(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ricklang(self, ctx, *, code):
        code = code.replace("`", "")

        output = await runner.run_code(code, "rickroll-lang", await_task=True)

        await ctx.send(
            embed=discord.Embed(
                title="Output",
                color=discord.Color.blue(),
                description=f"""```\n{output}\n```""",
                timestamp=datetime.datetime.now()
            )
        )


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
                        minutes = minutes - (hours*60)
                        time = f"{hours}h {minutes}min {seconds}s"
                return time

            cd = round(error.retry_after)
            if cd == 0:
                cd = 1
            retry_after = await better_time(cd)
            em = discord.Embed(
                title="Wow buddy, Slow it down\nThis command is on cooldown",
                description=f"Try again in **{retry_after}**",
                color=discord.Color.red()
            )
            em.timestamp = datetime.datetime.utcnow()
            error_msg = await ctx.send(embed=em)
            
            await ctx.message.add_reaction("⚠️")

        else:
            return

def setup(client):
    client.add_cog(Ricklang(client))