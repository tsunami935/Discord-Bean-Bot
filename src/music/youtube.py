from apiclient.discovery import build

class Youtube_Client:
    def __init__(self):
        self.__youtube = build('youtube','v3', developerKey = os.getenv("GOOGLE_TOKEN"))

    def get_video(self, query):
        '''Searches Youtube and returns video URL of first result'''
        search = self.__youtube.search().list(q=query, type="video", part="snippet").execute()
        try:
            video_id = search["items"][0]["id"]["videoId"]
            return "https://www.youtube.com/watch?v=" + video_id
        except:
            return None
            