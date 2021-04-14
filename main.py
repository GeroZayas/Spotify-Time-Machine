import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

# CONSTANTS
SPOTIFY_CLIENT_ID = "YOUR CLIENT ID"
SPOTIFY_CLIENT_SECRET_ID = "YOUR CLIENT SECRET ID"
URL = f"https://www.billboard.com/charts/hot-100/{date}"


# ---------------------- Scraping Billboard 100 ----------------------
response = requests.get(URL)
billboard_website = response.text

soup = BeautifulSoup(billboard_website, "html.parser")
# print(soup.prettify())

song_titles = soup.find_all(name='span', class_="chart-element__information__song text--truncate color--primary")
artist_names = soup.find_all(name='span', class_="chart-element__information__artist text--truncate color--secondary")

songs_list = []
artists_list = []

for song in song_titles:
    songs_list.append(song.getText())

for song in artist_names:
    artists_list.append(song.getText())

# print(songs_list, "\n")
# print(artists_list, "\n")

# Making a dictionary from these two lists
zip_iterator = zip(artists_list, songs_list)
artist_songs_dict = dict(zip_iterator)
# print(artist_songs_dict)

# ------------------- Spotify Authentication ---------------------
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET_ID,
        show_dialog=True,
        cache_path="token.txt" #You get this file once you follow through the authentication process https://spotipy.readthedocs.io/
    )
)
user_id = sp.current_user()["id"]
print("user id:", user_id)

# ------------- Searching Spotify for songs by title -----------------

song_uris = []
year = date.split("-")[0]
for song in songs_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# ---------- Creating a new private playlist in Spotify ----------------
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print(playlist)

# ------------- Adding songs found into the new playlist -------------------
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
