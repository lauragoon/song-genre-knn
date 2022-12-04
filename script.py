# import numpy as np
# import math
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = ""
CLIENT_SECRET = ""
TRAINING_PLAYLIST_ID = "1C49yxU1XBkoq5yaVDbJwx"
# TRAINING_PLAYLIST_IDS = {"Hip Hop": "1C49yxU1XBkoq5yaVDbJwx"}
TRAINING_DATA, TESTING_DATA = None, None

SP = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET))


def get_tracks(playlist_id):
    response = SP.playlist_items(playlist_id, fields=["total"])
    track_names_df = pd.DataFrame(columns=["id", "name"])
    num_tracks = response["total"]

    while track_names_df.shape[0] < num_tracks:
        response = SP.playlist_items(playlist_id, fields=["items.track.id, items.track.name"],
                                     offset=track_names_df.shape[0])
        tracks_response = response["items"]
        for track in tracks_response:
            if track is not None and track["track"] is not None and track["track"]["id"] is not None:
                temp_df = pd.DataFrame([track["track"]])
                track_names_df = pd.concat([temp_df, track_names_df])

    track_names_df = track_names_df.astype({"id": "string", "name": "string"})
    return track_names_df


def get_tracks_features(tracks):
    ids = tracks["id"].tolist()
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

    track_features_df.drop(columns=["type", "uri", "track_href", "analysis_url"], inplace=True)
    track_features_df = track_features_df.astype({"id": "string"})
    return track_features_df


def combine_track_data(track_names, track_features):
    track_names.drop_duplicates(subset=["id"], inplace=True)
    track_features.drop_duplicates(subset=["id"], inplace=True)

    combined_df = track_names.merge(track_features, on="id", how="inner")

    return combined_df


def main():
    training_track_names = get_tracks(TRAINING_PLAYLIST_ID)
    training_track_features = get_tracks_features(training_track_names)
    global TRAINING_DATA
    TRAINING_DATA = combine_track_data(training_track_names, training_track_features)


main()
