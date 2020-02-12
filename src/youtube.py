# import google.oauth2.credentials
# import google_auth_oauthlib.flow

# api_service_name = "youtube"
# api_version = "v3"
# client_secrets_file = "../.client_secret.json"
# scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


# flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#     client_secrets_file, 
#     scopes)

# flow.redirect_uri = 'https://www.example.com/oauth2callback'

# authorization_url, state = flow.authorization_url(
#     # Enable offline access so that you can refresh an access token without
#     # re-prompting the user for permission. Recommended for web server apps.
#     access_type='offline',
#     # Enable incremental authorization. Recommended as a best practice.
#     include_granted_scopes='true')
