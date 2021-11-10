import os
import asyncio
from discord.ext import tasks, commands
from discord import FFmpegPCMAudio
from discord.utils import get
from apiclient.discovery import build
from youtube_dl import YoutubeDL

class Music(commands.Cog):
    '''music commands'''
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        #initialize sources and clients
        self.__youtube = build('youtube','v3', developerKey = os.getenv("GOOGLE_TOKEN"))
        self.__sources = {"-y": 0, "-s": 1, "-c": 2}
        self.__valid_sources = ["https://www.youtube.com/watch?v=", "https://youtu.be/"]
        self.__get_URL = {
            0 : self.__get_YT_URL,
            1 : self.__get_spotify_URL,
            2 : self.__get_soundcloud_URL
        }
        self.player = 0
    
    async def __queuePlayer(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not len(self.queue) and not voice.is_playing():
            await self.stop(ctx)
            return
        if not voice.is_playing():
            song = self.queue.pop(0)
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
                self.player = 0
                return
            self.player = 1
            await ctx.send(f"Now playing {song['url']}")
        await self.__queuePlayer(ctx)

    async def __join(self, ctx):
        '''Joins voice channel if possible'''
        channel = ctx.message.author.voice.channel
        if channel == None:
            await ctx.send("You must be in a voice channel to play music!")
            return 0
        else:
            voice = get(self.bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                if voice.channel == channel:
                    return 1
                self.queue = [self.queue[-1]]
                await voice.move_to(channel)
                return 1
            else:
                voice = await channel.connect()
                return 1

    #play/add to queue
    @commands.command(name = "play")
    async def play(self, ctx):
        '''$b justin beiber baby
        Give URL or search term | sources: -y = YT, -s = Spotify, -c = Soundcloud (default: YT)
        Note: -s and -c currently unsupported and may be added in the future
        Note: URLS or searches for playlists are not allowed'''
        query = ctx.message.content[3:]
        URL, source = await self.get_URL(query)
        if URL == None:
            ctx.send("No results found :(")
        #add song to queue
        else:
            self.queue.append({
                "url" : URL,
                "source": source,
                "requester": ctx.author
            })
            await ctx.send(f"Added {URL} to queue [{len(self.queue)}]")
            await self.__join(ctx)
            if not self.player:
                await self.__queuePlayer(ctx) #make event loop async


    #stop
    @commands.command(name = "stop")
    async def stop(self, ctx):
        '''Stops playing music and leaves the call'''
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            print("is stopping")
            voice.stop()
            voice.disconnect()
            self.queue = []
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
                return input
        input, source = await self.__find_source(input)
        URL = await self.__get_URL[source](input[:-2])
        return URL, input[-2:]


class MusicManager():
    def __init__(self):
        #initialize Youtube client
        self.__youtube = build('youtube','v3', developerKey = os.getenv("GOOGLE_TOKEN"))
        self.__sources = {"-y": 0, "-s": 1, "-c": 2}
        self.__valid_sources = ["https://www.youtube.com/watch?v=", "https://youtu.be/"]
        self.__get_URL = {
            0 : self.__get_YT_URL,
            1 : self.__get_spotify_URL,
            2 : self.__get_soundcloud_URL
        }

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
                return input
        input, source = await self.__find_source(input)
        URL = await self.__get_URL[source](input[:-2])
        return URL

        