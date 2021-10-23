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
bot = commands.Bot(command_prefix='$b ', description=description)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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
    
    async def __join(self, ctx):
        '''Joins voice channel if possible'''
        channel = ctx.message.author.voice.channel
        if channel == None:
            await ctx.send("You must be in a voice channel to play music!")
        else:
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()

    #play/add to queue
    @commands.command(name = "play")
    async def play(self, ctx, *source):
        '''Give URL or search term | sources: -y = YT, -s = Spotify, -c = Soundcloud (default: YT)'''
        #determine if URL or search term
            #if URL, check if valid
            #else, check source
                #get URL
        #add song to queue

    #stop
    @commands.command(name = "stop")
    async def stop(self, ctx):
        '''Stops playing music and leaves the call'''
        pass

bot.add_cog(Music(bot))

if(__name__ == "__main__"):
    bot.run(DISCORD_TOKEN)
