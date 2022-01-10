from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

class Spotify_Client:
    def __init__(self):
        self.spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())

    def get_playlist(self, URL):
        playlist = self.spotify.playlist_items(URL, limit=60)
        queries = []
        for item in playlist['items']:
            queries.append(" ".join((item['track']['name'], item['track']['artists'][0]['name'])))
        return queries

#testing
def main():
    from dotenv import load_dotenv
    load_dotenv()
    spotify_client = Spotify_Client()
    q = spotify_client.get_playlist("https://open.spotify.com/playlist/12lPlz1OwScdlcJygN2038?si=a67ce5349d624701")
    for item in q:
        print(item)

if __name__ == "__main__":
    main()