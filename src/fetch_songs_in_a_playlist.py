import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("We need your username as sys.argv!")
    sys.exit()

try:
    playlists = sp.user_playlists(username)
    playlists_owned_by_user = [p for p in playlists if p['owner']['id'] == username]

    for playlist in playlists_owned_by_user:
        print(playlist['name'])
        print('  total tracks', playlist['tracks']['total'])
        # results = sp.playlist(playlist['id'], fields="tracks,next")
        # tracks = results['tracks']
        # show_tracks(tracks)
        # while tracks['next']:
        #     tracks = sp.next(tracks)
        #     show_tracks(tracks)
except Exception as e:
    print(f"Cannot fetch playlists of {username} because {e}.")
