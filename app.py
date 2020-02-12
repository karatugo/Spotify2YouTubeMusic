import os
import flask
import requests
import re

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from flask import Flask, render_template, request
from src.spoti import do_spoti, fetch_user_playlists

app = Flask(__name__)

# https://flask.palletsprojects.com/en/1.1.x/quickstart/#sessions
app.secret_key = 'your-secret-key'

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = ".client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template("index.html", head_title="Spotify 2 YouTube Music")

def get_song_youtube_ids(youtube, q):
    request = youtube.search().list(
        part="snippet",
        q=q,
        type="video"
    )

    search_response = request.execute()
    first_video_id = search_response["items"][0]["id"]["videoId"]
    return first_video_id


def insert_song_to_youtube_playlist(youtube, playlist_id, song_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": song_id
            }
          }
        }
    )

    add_song_response = request.execute()
    return flask.jsonify(add_song_response)

def do_s2ytm(youtube, spotify_username):
    playlist_artist_track_data = do_spoti(spotify_username)

    for playlist_data in playlist_artist_track_data:
        playlist_name = playlist_data["name"]
        create_youtube_playlist(youtube, playlist_name)
        playlist_youtube_id = search_youtube_playlist(youtube, playlist_name)
        
        youtube_song_ids = []

        for i in playlist_data["items"]:
            youtube_song_ids.append(get_song_youtube_ids(youtube, i["artist"] + " " + i["track"]))

        for song_id in youtube_song_ids:
            insert_song_to_youtube_playlist(youtube, playlist_youtube_id, song_id)

        break

@app.route('/s2ytm', methods=["POST", "GET"])
def s2ytm():
    if request.method == "POST":
        flask.session["spotify_username"] = request.form["spotify_username"]
        spotify_username = flask.session["spotify_username"]
    elif flask.session["spotify_username"]:
        spotify_username = flask.session["spotify_username"]
    else:
        return redirect("/")
    
    if 'credentials' not in flask.session:
        return flask.redirect("authorize")

    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials) 
    flask.session['credentials'] = credentials_to_dict(credentials)

    try:
        do_s2ytm(youtube, spotify_username)
        return "<p>Yaaay! All done! Check it out <a href='https://www.youtube.com/view_all_playlists?nv=1'>here</a></p>"
    except Exception as e:
        return f"<p>{spotify_username}, we have a problem. Check your playlists <a href='https://www.youtube.com/view_all_playlists?nv=1'>here</a>.</p><p>PS. YouTube says that <i>" + re.sub('[^A-Za-z0-9 ]+', '', str(e)) + "</i>.</p><p>Yeah, whatever...</p>"


def search_youtube_playlist(youtube, playlist_name):
    request = youtube.playlists().list(
        part="snippet",
        mine=True
    )

    search_response = request.execute()
    return [item["id"] for item in search_response["items"] if item["snippet"]["title"] == playlist_name]


def create_youtube_playlist(youtube, playlist_name):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": playlist_name,
            "description": f"The playlist {playlist_name} moved from Spotify.",
            "tags": [
              "sample playlist",
              "API call"
            ],
            "defaultLanguage": "en"
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    create_youtube_playlist_response = request.execute()
    
    return flask.jsonify(create_youtube_playlist_response)


@app.route('/youtube')
def youtube():
    return print_index_table()

@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Search for a song
    request = youtube.search().list(
        part="snippet",
        q="Waltz in A minor",
        type="video"
    )

    search_response = request.execute()

    first_video_id = search_response["items"][0]["id"]["videoId"]

    # Add songs to a playlist
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": "PL3AgsfiW8ntWXfIKnARk2jyhP1xDM4-oL",
            "resourceId": {
              "kind": "youtube#video",
              "videoId": first_video_id
            }
          }
        }
    )

    add_song_response = request.execute()

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(add_song_response)


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')


    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect("/s2ytm")


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
