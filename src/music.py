import os
import asyncio
from time import time
from discord.ext import tasks, commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.utils import get
from apiclient.discovery import build
from youtube_dl import YoutubeDL

class Server_Instance():
    def __init__(self):
        self.default()
    
    def default(self):
        self.queue = []
        self.player = 0
        self.pause = None

class Music(commands.Cog):
    '''music commands'''
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}
        #initialize sources and clients
        self.__youtube = build('youtube','v3', developerKey = os.getenv("GOOGLE_TOKEN"))
        self.__sources = {"-y": 0, "-s": 1, "-c": 2}
        self.__valid_sources = ["https://www.youtube.com/watch?v=", "https://youtu.be/"]
        self.__get_URL = {
            0 : self.__get_YT_URL,
            1 : self.__get_spotify_URL,
            2 : self.__get_soundcloud_URL
        }
    
    async def __queuePlayer(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if self.guilds[ctx.guild.id].pause:
            if time() - self.guilds[ctx.guild.id].pause >= 300:
                await self.stop(ctx)
                return
        elif not len(self.guilds[ctx.guild.id].queue) and not voice.is_playing():
            self.guilds[ctx.guild.id].pause = time()
        elif not voice.is_playing():
            song = self.guilds[ctx.guild.id].queue.pop(0)
            print(song)
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(song['url'], download=False)
            URL = info['url']
            try:
                voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                voice.is_playing()
            except:
                self.guilds[ctx.guild.id].player = 0
                return
            self.guilds[ctx.guild.id].player = 1 
            await ctx.send(f"Now playing {song['url']}")

    async def __playerLoop(self, ctx):
        while self.guilds[ctx.guild.id].player: 
            await self.__queuePlayer(ctx)
            await asyncio.sleep(5)

    async def __join(self, ctx):
        '''Joins voice channel if possible'''
        try:
            channel = ctx.message.author.voice.channel
            if channel == None:
                await ctx.send("You must be in a voice channel to play music!")
                return 0
        except:
            await ctx.send("You must be in a voice channel to play music!")
            return 0
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            if voice.channel == channel:
                return 1
            self.guilds[ctx.guild.id].queue = [self.guilds[ctx.guild.id].queue[-1]] 
            await voice.move_to(channel)
            return 1
        else:
            voice = await channel.connect()
            await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            return 1

    #play/add to queue
    @commands.command(name = "play")
    async def play(self, ctx):
        '''$b justin beiber baby
        Give URL or search term | sources: -y = YT, -s = Spotify, -c = Soundcloud (default: YT)
        Note: -s and -c currently unsupported and may be added in the future
        Note: URLS or searches for playlists are not allowed'''
        query = ctx.message.content[8:]
        URL, source = await self.get_URL(query)
        if URL == None:
            await ctx.send("No results found :(")
        #add song to queue
        else:
            join = await self.__join(ctx)
            if join:
                if ctx.guild.id not in self.guilds:
                    self.guilds[ctx.guild.id] = Server_Instance()
                self.guilds[ctx.guild.id].queue.append({ 
                    "url" : URL,
                    "source": source,
                    "requester": ctx.author
                })
                if not self.guilds[ctx.guild.id].player: 
                    self.guilds[ctx.guild.id].player = 1 
                    asyncio.create_task(self.__playerLoop(ctx))
                else:
                    await ctx.send(f"Added {URL} to queue [{len(self.guilds[ctx.guild.id].queue)}]")

    #next
    @commands.command(name = "next", aliases = ["skip"])
    async def next(self, ctx):
        '''Skips to the next song in queue if possible'''
        if len(self.guilds[ctx.guild.id].queue):
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            voice.stop()
            await self.__queuePlayer(ctx)
        else:
            await ctx.send("There is no song to skip to. Try using 'stop' or 'pause' instead or adding another song to the queue.")

    #pause
    @commands.command(name = "pause")
    async def pause(self, ctx):
        '''Pauses the current song'''
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
            self.guilds[ctx.guild.id].pause = time()

    #resume
    @commands.command(name = "resume")
    async def resume(self, ctx):
        '''Resumes playing the current song'''
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            voice.resume()
            self.guilds[ctx.guild.id].pause = None

    #stop
    @commands.command(name = "stop")
    async def stop(self, ctx):
        '''Stops playing music and leaves the call'''
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice:
            print("is stopping")
            voice.stop()
            await voice.disconnect()
            self.guilds[ctx.guild.id].default()
            await ctx.send("Adios!")

    #private methods and utilities
    async def __find_source(self, input):
        try:
            source = self.__sources[input[-2:]]
            return input, source
        except:
            source = self.__sources["-y"]
            return input + "-y", source
    
    async def __get_YT_URL(self, query):
        '''searches YouTube and returns URL of first result'''
        search = self.__youtube.search().list(q=query, type="video", part="snippet").execute()
        try:
            print(f"YT query: {query}")
            video_id = search["items"][0]["id"]["videoId"]
            URL = self.__valid_sources[0] + video_id
            return URL
        except:
            return None

    async def __get_spotify_URL(self, query):
        '''searches spotify and returns URL of first result'''
        print(f"__get_spotify_URL({query}) called; function still incomplete")
        return None

    async def __get_soundcloud_URL(self, query):
        '''searches soundcloud and returns URL of first result'''
        print(f"__get_soundcloud_URL({query}) called; function still incomplete")
        return None

    async def get_URL(self, input):
        '''checks input'''
        for s in self.__valid_sources:
            if len(input) > len(s) and input.startswith(s):
                return input, 0
        input, source = await self.__find_source(input)
        URL = await self.__get_URL[source](input[:-2])
        return URL, input[-2:]