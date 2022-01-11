import asyncio
from time import time
from random import shuffle
from discord.ext import tasks, commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.utils import get
from youtube_dl import YoutubeDL

from music.youtube import Youtube_Client
from music.spotify import Spotify_Client

class Server_Instance():
    def __init__(self):
        self.default()
    
    def default(self):
        self.queue = []
        self.player = 0
        self.pause = None
        self.user_pause = False

class Music(commands.Cog):
    '''music commands'''
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}
        #initialize sources and clients
        self.__youtube = Youtube_Client()
        self.__spotify = Spotify_Client()
        self.__valid_sources = ["https://www.youtube.com/watch?v=", "https://youtu.be/", "https://open.spotify.com/"]

    #play/add to queue
    @commands.command(name = "play")
    async def play(self, ctx):
        '''Give URL or search term of song or URL of playlist
        Note: Youtube playlists are currently unsupported'''
        query = ctx.message.content.strip("$b play ")
        results = await self.get_URL(query) #
        if results[0] == None:
            await ctx.send("No results found :(")
        #add songs to queue
        else:
            join = await self.__join(ctx)
            if join:
                if ctx.guild.id not in self.guilds:
                    self.guilds[ctx.guild.id] = Server_Instance()
                for track in results:
                    if track:
                        self.guilds[ctx.guild.id].queue.append({
                            'url': track['url'],
                            'title': track['title'],
                            'length': track['length'],
                            'request': ctx.message.author
                        })
                if len(results) > 1:
                    await ctx.send(f"Added `{len(results)}` songs to the queue")
                if not self.guilds[ctx.guild.id].player: 
                    self.guilds[ctx.guild.id].player = 1 
                    asyncio.create_task(self.__playerLoop(ctx))
                else:
                    if len(results) == 1:
                        await ctx.send(f"Added [ **{results[0]['title']}** ] `({results[0]['length']})` to queue [{len(self.guilds[ctx.guild.id].queue)}]")

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
            self.guilds[ctx.guild.id].user_pause = True

    #resume
    @commands.command(name = "resume")
    async def resume(self, ctx):
        '''Resumes playing the current song'''
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            voice.resume()
            self.guilds[ctx.guild.id].pause = None
            self.guilds[ctx.guild.id].user_pause = False

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

    #volume
    @commands.command(name = "volume")
    async def volume(self, ctx):
        '''Adjust volume of the bot (1-200) // $b volume will return current volume'''
        val = ctx.message.content.strip("$b volume ")
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            return
        if not len(val):
            try:
                curr = ((voice.source.volume) * 100) // 1
            except:
                curr = 100
            await ctx.send(f"Current volume: {curr}%")
            return
        elif val.isdigit() and 0 <= int(val) <= 200:
            if hasattr(voice.source, "volume"):
                voice.source.volume = int(val) / 100
            else:
                voice.source = PCMVolumeTransformer(voice.source, int(val) / 100)
            await ctx.send(f"Volume set to {val}")
            return
        await ctx.send("Bot takes a value from 1-200")

    #shuffle
    @commands.command(name = "shuffle")
    async def queue_shuffle(self, ctx):
        '''Shuffles the queue'''
        self.guilds[ctx.guild.id].queue.shuffle()
        await ctx.send("Queue shuffled")

    #private methods and utilities
    async def __queuePlayer(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if len(voice.channel.members) == 0:
            await ctx.send("Leaving due to inactivity")
            await self.stop(ctx)
        if self.guilds[ctx.guild.id].pause:
            if self.guilds[ctx.guild.id].user_pause == False and len(self.guilds[ctx.guild.id].queue):
                self.guilds[ctx.guild.id].pause = False
                await self.__playYT(voice, ctx)
            elif time() - self.guilds[ctx.guild.id].pause >= 300:
                await ctx.send("Leaving due to inactivity")
                await self.stop(ctx)
                return
        elif not len(self.guilds[ctx.guild.id].queue) and not voice.is_playing():
            self.guilds[ctx.guild.id].pause = time()
        elif not voice.is_playing():
            await self.__playYT(voice, ctx)

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
            if len(self.guilds[ctx.guild.id].queue):
                self.guilds[ctx.guild.id].queue = [self.guilds[ctx.guild.id].queue[-1]]
            await voice.move_to(channel)
            return 1
        else:
            voice = await channel.connect()
            await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            return 1

    async def get_URL(self, input):
        '''Returns list of URLs'''
        for s in self.__valid_sources[:2]: #direct YT video link
            if len(input) > len(s) and input.startswith(s):
                return [input]
        for s in self.__valid_sources[2:]: #spotify links
            if len(input) > len(s) and input.startswith(s):
                queries = self.__spotify.process(input)
                for i in range(len(queries)):
                    queries[i] = await self.__youtube.search_video(queries[i])
                return queries
        return [await self.__youtube.search_video(input)] #YT search

    async def __playYT(self, voice, ctx):
        song = self.guilds[ctx.guild.id].queue.pop(0)
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
        await ctx.send(f"Now playing [ **{song['title']}** ] `({song['length']})`")