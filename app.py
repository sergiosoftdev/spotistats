from flask import Flask, render_template, session, url_for, redirect, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import base64
import tempfile
import os


CLIENT_ID = "8cd8a6d7b96940e4ae03d033664a1ba3"
CLIENT_ID_SECRET = "4d4c1a4aaa6b41d3bed12d62166dd080"

app = Flask(__name__)
app.secret_key = CLIENT_ID_SECRET



def spotifyauth():
    # Especifica una ubicación para la caché (archivo temporal)
    cache_path = os.path.join(tempfile.gettempdir(), "spotipy_cache")

    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_ID_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-top-read",
        cache_path=cache_path,  # Agrega la opción cache_path
    )
    
def clear_cache():
    cache_path = os.path.join(tempfile.gettempdir(), "spotipy_cache")
    try:
        os.remove(cache_path)
    except FileNotFoundError:
        pass
    
def revoke_token(access_token):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_ID_SECRET}".encode()).decode(),
    }
    data = {
        "token": access_token,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.status_code


@app.route('/', methods=["POST", "GET"])
def index():

    if request.method =="GET":
        return render_template("index.html", session=session)
    else:
        return redirect("/login")
    

@app.route('/login', methods=["GET", "POST"])
def login():

    sp_oauth = spotifyauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url) 
    return redirect(auth_url)

@app.route('/redirectPage')
def redirectPage():

    sp_oauth = spotifyauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["TOKEN_INFO"] = token_info

    return redirect(url_for("allTimeSongs", _external=True))

def get_token():

    token_info = session.get("TOKEN_INFO", None)
    return token_info

@app.route('/alltimesongs')
def allTimeSongs():

    try:

        if "TOKEN_INFO" in session:

            user_token = get_token()
            sp = spotipy.Spotify(auth=user_token['access_token'])

            usershortsongs = sp.current_user_top_tracks(limit=25, offset=0, time_range="long_term")
            usershortsongs["items"][0]["album"]["images"][0]["url"]

            return render_template("songs.html", songs=usershortsongs['items'], time="Top Songs: All time")
        
        else:

            return redirect("/login")


    
    except(spotipy.SpotifyException):

        return redirect("/login")
    
@app.route('/mediumsongs')
def mediumsongs():

    try:

        if "TOKEN_INFO" in session:

            user_token = get_token()
            sp = spotipy.Spotify(auth=user_token['access_token'])

            usershortsongs = sp.current_user_top_tracks(limit=25, offset=0, time_range="medium_term")
            usershortsongs["items"][0]["album"]["images"][0]["url"]

            return render_template("songs.html", songs=usershortsongs['items'], time="Top Songs: Last 6 months")
        
        else:

            return redirect("/login")


    
    except(spotipy.SpotifyException):

        return redirect("/login")
    
    
@app.route('/shortsongs')
def shortsongs():

    try:

        if "TOKEN_INFO" in session:

            user_token = get_token()
            sp = spotipy.Spotify(auth=user_token['access_token'])

            usershortsongs = sp.current_user_top_tracks(limit=25, offset=0, time_range="short_term")
            usershortsongs["items"][0]["album"]["images"][0]["url"]

            return render_template("songs.html", songs=usershortsongs['items'], time="Top Songs: Last 4 weeks")
        
        else:

            return redirect("/login")


    
    except(spotipy.SpotifyException):

        return redirect("/login")
    
@app.route('/alltimeartists')
def allTimeArtists():

    try:

        if "TOKEN_INFO" in session:

            user_token = get_token()
            sp = spotipy.Spotify(auth=user_token['access_token'])

            userlongartists = sp.current_user_top_artists(limit=25, offset=0, time_range="long_term")
            print(userlongartists["items"][0]["images"][0]["url"])

            return render_template("artists.html", artists=userlongartists, time="Top Artists: All time")

        else:

            return redirect("/login")

    except(spotipy.SpotifyException):

        return redirect("/login")
    
@app.route('/mediumartists')
def mediumartists():

    try:

        if "TOKEN_INFO" in session:

            user_token = get_token()
            sp = spotipy.Spotify(auth=user_token['access_token'])

            userlongartists = sp.current_user_top_artists(limit=25, offset=0, time_range="medium_term")
            print(userlongartists["items"][0]["images"][0]["url"])

            return render_template("artists.html", artists=userlongartists, time="Top Artists: Last 6 months")

        else:

            return redirect("/login")

    except(spotipy.SpotifyException):

        return redirect("/login")
    
    
@app.route('/shortartists')
def shortartists():

    try:

        if "TOKEN_INFO" in session:

            user_token = get_token()
            sp = spotipy.Spotify(auth=user_token['access_token'])

            userlongartists = sp.current_user_top_artists(limit=25, offset=0, time_range="short_term")
            print(userlongartists["items"][0]["images"][0]["url"])

            return render_template("artists.html", artists=userlongartists, time="Top Artists: Last 6 months")

        else:

            return redirect("/login")

    except(spotipy.SpotifyException):

        return redirect("/login")
    
@app.route('/logout')
def logout():
    # Limpiar la caché de inicio de sesión en Spotify
    clear_cache()

    token_info = session.get("token_info", None)
    if token_info:
        access_token = token_info.get("access_token", None)
        if access_token:
            # Revocar el token de acceso antes de eliminarlo de la sesión
            revoke_token(access_token)

    # Eliminar el token de acceso almacenado en la sesión
    session.pop("TOKEN_INFO", None)

    return redirect("/")

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000, host='0.0.0.0')

