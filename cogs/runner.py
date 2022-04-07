import os
import string
import random
import asyncio
import datetime
from subprocess import run
from distutils.dir_util import copy_tree

import shutil
import discord
from discord.ext import commands

class Ricklang(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    # @commands.cooldown(1, 60, commands.BucketType.user)
    async def ricklang(self, ctx, *, code):
        code = code.replace("`", "")
        
        random_code_list = string.ascii_lowercase + string.digits
        random_code = "".join([random.choice(random_code_list) for i in range(12)])
        print(random_code)
        os.mkdir(f"./files/{random_code}")

        with open(f"./files/{random_code}/main.rickroll", "w") as f:
            f.write(code)

        with open(f"./files/{random_code}/Dockerfile", "w") as f:
            f.write(
"""

FROM ricklang

COPY main.rickroll .

CMD ["python3", "RickRoll.py", "main.rickroll"]

"""
            )

        copy_tree(f"{os.getcwd()}/files/src-py/", f"{os.getcwd()}/files/{random_code}/src-py/")

        build = run(["docker", "build", "-t", random_code, f"./files/{random_code}"])
        output = run(["timeout", "-s", "KILL", "3", "docker", "run", "--rm", "--read-only", random_code], capture_output=True).stdout.decode()
        if len(output) > 4000:
            output = output[:4000]
        await ctx.send(
            embed=discord.Embed(title = "Output", color=discord.Color.blue(), description=f"""```\n{output}\n```""")
        )
        shutil.rmtree(f"./files/{random_code}")
        
        await asyncio.sleep(10)

        image = run(["docker", "images", "-q", random_code], capture_output=True).stdout.decode()
        os.system(f"docker image rm -f {image}")

        container = run([f"docker ps -a -q  --filter ancestor={image}"], capture_output=True).stdout.decode()
        run([f"docker container kill {container}"])



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