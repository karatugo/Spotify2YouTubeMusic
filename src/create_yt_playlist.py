# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlists.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "../.client_secret.json"

    # Get credentials and create an API client
    if os.path.isfile("../.credentials.json"):
        with open("../.credentials.json", 'r') as f:
            creds_data = json.load(f)
        credentials = creds_data #Credentials(creds_data['token'])
        print("****************")
    else:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console(access_type='offline', include_granted_scopes='true')
        creds_data = {
              'token': credentials.token,
              'refresh_token': credentials.refresh_token,
              'token_uri': credentials.token_uri,
              'client_id': credentials.client_id,
              'client_secret': credentials.client_secret,
              'scopes': credentials.scopes
          }
        #print(creds_data)
        with open("../.credentials.json", 'w') as outfile:
          json.dump(creds_data, outfile)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.playlists().insert(
        part="snippet,status",
        body={
          "snippet": {
            "title": "Sample playlist created via API3",
            "description": "This is a sample playlist description.",
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
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()