import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

client_credentials_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def show_tracks(tracks):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))

def fetch_songs_in_a_playlist(playlist):
    p = {
        "name": playlist['name'],
        "items": []
    }
    # print("Playlist name: " + playlist['name'])
    # print('  total tracks', playlist['tracks']['total'])
    
    results = spotify.playlist(playlist['id'], fields="tracks,next")

    for i, item in enumerate(results["tracks"]['items']):
        track = item['track']
        # print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))
        p["items"].append(
            {
                "artist": track['artists'][0]['name'],
                "track": track['name'] 
            }
        )

    # print(json.dumps(p, indent=4))
    return p
    
    # tracks = results['tracks']
    # show_tracks(tracks)
    # while tracks['next']:
    #     tracks = spotify.next(tracks)
    #     show_tracks(tracks)

def fetch_user_playlists(username):
    try:
        return spotify.user_playlists(username)
    except Exception as err:
        print(f"Cannot fetch playlists of {username} because {err}.")

def do_spoti(username):
    playlists = fetch_user_playlists(username)   
    playlists_owned_by_user = [p for p in playlists["items"] if p["owner"]["id"] == username]
    # return [p["name"] for p in playlists_owned_by_user]
    playlist_artist_track_data = []
    for playlist in playlists_owned_by_user:
        playlist_artist_track_data.append(fetch_songs_in_a_playlist(playlist))

    return playlist_artist_track_data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("We need your username as sys.argv!")
        sys.exit()

    do_spoti(username)
