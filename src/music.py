import os
from apiclient.discovery import build

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
        
        