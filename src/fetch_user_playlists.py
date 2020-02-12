import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("We need your username as sys.argv!")
    sys.exit()

try:
    return spotify.user_playlists(username)
    # for playlist in playlists['items']:
    #     print(playlist['name'])
except:
    print(f"Cannot fetch playlists of {username}")
    return None