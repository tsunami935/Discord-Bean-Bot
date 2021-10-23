#imports
import os
import sys
from datetime import datetime as dt
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands
from discord.utils import get
from youtube_dl import YoutubeDL

#load environment variables
load_dotenv()

#initialize client
description = '''This is Bean. Bean is bot'''
bot = commands.Bot(command_prefix='s! ', description=description)
TOKEN = os.getenv('DISCORD_TOKEN')

#on ready
@bot.event
async def on_ready():
    activity = discord.Game("$b for Bean! | PapaPutin#4943 is indeed my father")
    await bot.change_presence(activity=activity)
    print(f'{bot.user.name} has connected successfully!')

#music commands
class Music(commands.Cog):
    '''music commands'''
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    #play/add to queue
    @commands.command(name = "play")
    async def play(self, ctx, *source):
        '''Give URL or search term | sources: -y = YT, -s = Spotify, -c = Soundcloud (default: YT)'''
