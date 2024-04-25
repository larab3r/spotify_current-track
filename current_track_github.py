import requests
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'SESSION_COOKIE'
app.secret_key = 'SECRET_KEY'
TOKEN_INFO = 'token_info'


# route to handle logging in
@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

# route to handle the redirect URI after authorization
@app.route('/spotify_redirect')
def spotify_redirect():
    session.clear()
    code = request.args.get('code') # get the authorization code from the request parameters
    token_info = create_spotify_oauth().get_access_token(code) # exchange the authorization code for an access token and refresh token
    session[TOKEN_INFO] = token_info
    return redirect(url_for('display_current_song', _external=True))

# route to display the user's current song
@app.route('/display_current_song')
def display_current_song():
    try:
        token_info = get_token()
    except:
        # if the token info is not found, redirect the user to the login route
        print("User not logged in.")
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])

    try:
        current_track = sp.current_user_playing_track()['item']
        track_id = current_track['id']
        track_name = current_track['name']
        artists = current_track['artists']
        artist_names = ', '.join([artist['name'] for artist in artists])
        link = current_track['external_urls']['spotify']

        current_track_info = {
            "id": track_id,
            "name": track_name,
            "artists": artist_names,
            "link": link
        }

        return current_track_info
    except:
        return "User is not currently playing anything."



# gets the token info from the session
def get_token():
    token_info = session.get(TOKEN_INFO)
    if not token_info:
        return redirect(url_for('login'), _external=False)
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

# creates a Spotify OAuth
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id='CLIENT_ID',
        client_secret='CLIENT_SECRET',
        redirect_uri=url_for('spotify_redirect', _external=True),
        scope='user-read-currently-playing',
    )



def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
