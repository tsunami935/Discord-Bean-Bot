from youtubesearchpython.__future__ import VideosSearch, Playlist
import re

class Youtube_Client:
    def __init__(self):
        pass
    
    async def search_video(self, query):
        '''Searches Youtube and returns the first result'''
        search = VideosSearch(query, limit=1)
        video = await search.next()
        return  {
            'url' : video['result'][0]['link'],
            'title' : video['result'][0]['title'],
            'length' : video['result'][0]['duration']
        }

    async def get_playlist(self, playlist_link):
        '''Returns a list of videos in a Youtube playlist given the playlist URL'''
        try:
            playlist = await Playlist.getVideos(playlist_link)
            if len(playlist['videos']) == 0:
                return [None]
            res = []
            for video in playlist['videos']:
                res.append({
                    'url' : video['link'],
                    'title' : video['title'],
                    'length' : video['duration']
                })
            return res
        except:
            return [None]

    #private methods
    async def __check_privacy(self, link):
        if await Playlist.getInfo(link):
            return False
        return True

    def __parse_title(self, title):
        for key in self.__strs.keys():
            if key in title:
                title = title.replace(key, self.__strs[key])
        return title
    
    def __parse_duration(self, duration):
        return re.sub("[^0-9.]", ":", duration)

            
#testing
def main():
    from dotenv import load_dotenv
    load_dotenv()
    yt = Youtube_Client()
    print(yt.get_video("Gawr Gura Love Story"))

if __name__ == "__main__":
    main()