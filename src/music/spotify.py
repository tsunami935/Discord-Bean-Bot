from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

class Spotify_Client:
    def __init__(self):
        self.__spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.__sources = {
            "playlist": self.__get_playlist,
            "track": self.__get_track
        }

    def process(self, URL):
        '''Takes a valid spotify URL and returns a list of track strings'''
        for s in self.__sources.keys():
            if s in URL:
                return self.__sources[s](URL)
        return None

    #private methods
    def __get_playlist(self, URL):
        '''Takes a URI of spotify playlist and returns a list of track strings'''
        '''URL: any acceptable spotify URI'''
        playlist = self.__spotify.playlist_items(URL, limit=60)
        queries = []
        for item in playlist['items']:
            queries.append(" ".join((item['track']['name'], item['track']['artists'][0]['name'])))
        return queries
    
    def __get_track(self, URL):
        '''Takes a URI of spotify track and returns the track as a single item in a list'''
        '''URL: any acceptible spotify URI'''
        song = self.__spotify.track(URL)
        return [" ".join((song['name'], song['artists'][0]['name']))]

#testing
def main():
    from dotenv import load_dotenv
    load_dotenv()
    spotify_client = Spotify_Client()
    q = spotify_client.process("")
    for item in q:
        print(item)

if __name__ == "__main__":
    main()