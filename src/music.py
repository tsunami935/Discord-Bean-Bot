import os
from apiclient.discovery import build

class MusicManager():
    def __init__(self):
        #initialize Youtube client
        self.youtube = build('youtube','v3', developerKey = os.getenv("GOOGLE_TOKEN"))
        self.sources = {"-y": 0, "-s": 1, "-c": 2}
        self.valid_sources = ["https://www.youtube.com/watch?v=", "https://youtu.be/"]
        self.get_URL = {
            0 : self.__get_YT_URL,
            1 : self.__get_spotify_URL,
            2 : self.__get_soundcloud_URL
        }

    async def __find_source(self, input):
        try:
            source = self.sources[input[-2:]]
        except:
            source = self.sources["-y"]
        return source
    
    async def __get_YT_URL(self, query):
        '''searches YouTube and returns URL of first result'''
        search = self.youtube.search().list(q=query, type='video').execute()
        try:
            video_id = search["items"][0]["id"]["video_id"]
            URL = valid_sources[0] + video_id
            return URL
        except:
            return None


    async def get_URL(self, input):
        '''checks input'''
        for s in self.valid_sources:
            if input.startswith(s):
                return input
        source = await self.__find_source(input)
        URL = await self.get_URL[source](self, input[:-2])
        return URL
        
        