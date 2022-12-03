# import numpy as np
# import math
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = ""
CLIENT_SECRET = ""
TRAINING_PLAYLIST_ID = "1C49yxU1XBkoq5yaVDbJwx"
TRAINING_DATA = pd.DataFrame(columns=["ID", "Name", "Danceability", "Energy", "Key", "Loudness", "Mode", "Speechiness",
                                      "Acousticness", "Instrumentalness", "Liveness", "Valence", "Tempo",
                                      "Duration (ms)", "Time Signature"])
TESTING_DATA = pd.DataFrame(columns=["ID", "Name", "Danceability", "Energy", "Key", "Loudness", "Mode", "Speechiness",
                                     "Acousticness", "Instrumentalness", "Liveness", "Valence", "Tempo",
                                     "Duration (ms)", "Time Signature"])

SP = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET))


def get_tracks(playlist_id):
    response = SP.playlist_items(playlist_id, fields=["total"])
    tracks = []
    num_tracks = response["total"]

    while len(tracks) < num_tracks:
        response = SP.playlist_items(playlist_id, fields=["items.track.id, items.track.name"], offset=len(tracks))
        tracks_response = response["items"]
        for track in tracks_response:
            if track["track"]["id"] is not None:
                tracks.append([track["track"]["id"], track["track"]["name"]])

    return pd.DataFrame(tracks, columns=["ID", "Name"])


def get_tracks_features(tracks):
    ids = tracks["ID"].tolist()
    num_processed = 0
    track_features_df = None

    while num_processed < len(tracks):
        end_idx = num_processed + 50 if num_processed + 50 < len(tracks) else len(tracks)
        track_features = SP.audio_features(ids[num_processed:end_idx])

        if track_features_df is None:
            track_features_df = pd.DataFrame(track_features)
        else:
            temp_df = pd.DataFrame(track_features)
            track_features_df = pd.concat([temp_df, track_features_df])

        num_processed += 50

    return track_features_df


def main():
    training_tracks = get_tracks(TRAINING_PLAYLIST_ID)
    training_tracks_features = get_tracks_features(training_tracks)
    # print(TRAINING_DATA.head())
    # print(TRAINING_DATA.size)
  
  
main()
