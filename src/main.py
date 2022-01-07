#imports
import os
import sys
from datetime import datetime as dt
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
from discord.utils import get

from music import Music
from minigames import Minigames

#load environment variables
load_dotenv()

#initialize client
description = '''This is Bean. Bean is bot'''
bot = commands.Bot(command_prefix='$b ', description=description)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

#on ready
@bot.event
async def on_ready():
    activity = discord.Game("$b for Bean! | PapaPutin#4943 is indeed my father")
    await bot.change_presence(activity=activity)
    print(f'{bot.user.name} has connected successfully!')

@bot.event
async def on_guild_join(guild):
    role = await guild.create_role(name="Bean", colour=0x67B664)
    bot_user = guild.get_member(bot.user.id)
    await bot_user.add_roles(role)

@bot.command()
async def hi(ctx):
    await ctx.send(f'Hi {ctx.message.author.mention}!')

@bot.command()
async def bye(ctx):
    await ctx.send(f'Bye {ctx.message.author.mention}!')

bot.add_cog(Music(bot))
bot.add_cog(Minigames(bot))

if(__name__ == "__main__"):
    bot.run(DISCORD_TOKEN)
