import numpy as np
import math
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = ""
CLIENT_SECRET = ""
TEST_PLAYLIST_URL = "spotify:playlist:1C49yxU1XBkoq5yaVDbJwx"

sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET))


def main():
    response = sp.playlist_tracks(TEST_PLAYLIST_URL, fields=['items.track.name,total'])
  
  
main()
