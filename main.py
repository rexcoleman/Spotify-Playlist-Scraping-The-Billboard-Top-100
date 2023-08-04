from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os


SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
date = input("What year do you want to travel to?  Type the date in this format YYYY-MM-DD: ")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
billboard_hot_100_page = response.text
soup = BeautifulSoup(billboard_hot_100_page, "html.parser")

song_names_spans = soup.select("li ul li h3")

song_names = [song.getText().strip() for song in song_names_spans]
print(song_names)

song_uris = []
year = date.split("-")[0]



for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False, collaborative=False)
playlist_id = playlist["id"]
pprint(playlist)
top_100_playlist = sp.playlist_add_items(playlist_id=playlist_id, items=song_uris)
playlist_items = sp.playlist_items(playlist_id=playlist_id)
