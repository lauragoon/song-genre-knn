# import numpy as np
# import math
import pandas as pd
from sklearn import datasets
from sklearn.feature_selection import chi2, SelectKBest
from sklearn.preprocessing import MinMaxScaler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = ""
CLIENT_SECRET = ""
TRAINING_PLAYLIST_IDS = {"Hip Hop": "37i9dQZF1EQnqst5TRi17F", "Pop": "37i9dQZF1EQncLwOalG3K7",
                         "Country": "37i9dQZF1EQmPV0vrce2QZ", "Latin": "37i9dQZF1EQmK1rjZuPGDt",
                         "Rock": "37i9dQZF1EQpj7X7UK8OOF", "Dance/Electronic": "37i9dQZF1EQp9BVPsNVof1",
                         "Indie": "37i9dQZF1EQqkOPvHGajmW", "R&B": "37i9dQZF1EQoqCH7BwIYb7",
                         "Christian": "37i9dQZF1EQqZgBURAEzWH", "K-Pop": "37i9dQZF1EQpesGsmIyqcW",
                         "Metal": "37i9dQZF1EQpgT26jgbgRI", "Jazz": "37i9dQZF1EQqA6klNdJvwx",
                         "Classical": "37i9dQZF1EQn1VBR3CMMWb", "Folk & Acoustic": "37i9dQZF1EQp62d3Dl7ECY",
                         "Soul": "37i9dQZF1EQntZpEGgfBif", "Punk": "37i9dQZF1EQqlvxWrOgFZm",
                         "Blues": "37i9dQZF1EQpz3DZCEoX3g", "Afrobeats": "37i9dQZF1EQqFPe2ux3rbj",
                         "Funk": "37i9dQZF1EQnJyHBkXpASl"}
NUM_FEATURES = 5

SP = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET))


def get_track_names(playlist_ids):
    track_names_df = pd.DataFrame(columns=["id", "name", "genre"])

    for genre_name, genre_id in playlist_ids.items():
        response = SP.playlist_items(genre_id, fields=["items.track.id, items.track.name"])
        tracks_response = response["items"]
        for track in tracks_response:
            if track is not None and track["track"] is not None and track["track"]["id"] is not None:
                track["track"]["genre"] = genre_name
                temp_df = pd.DataFrame([track["track"]])
                track_names_df = pd.concat([temp_df, track_names_df])

    track_names_df = track_names_df.astype({"id": "string", "name": "string", "genre": "string"})
    return track_names_df


def get_track_features(tracks):
    ids = tracks["id"].tolist()
    num_processed = 0
    track_features_df = None

    while num_processed < len(tracks):
        end_idx = num_processed + 50 if num_processed + 50 < len(tracks) else len(tracks)
        track_features = SP.audio_features(ids[num_processed:end_idx])
        track_features = list(filter(lambda item: item is not None, track_features)) # filter Nones

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


def normalize_features(training_data):
    """
    Using Min-Max feature scaling method.
    """
    features_to_normalize = ["key", "loudness", "tempo", "duration_ms", "time_signature"]
    training_data[features_to_normalize] = MinMaxScaler().fit_transform(training_data[features_to_normalize])

    return training_data


def select_features(training_data):
    """
    Using Chi-Squared test.
    """
    X = training_data.iloc[:, 3:]
    y = training_data.iloc[:, 2:3]

    test = SelectKBest(score_func=chi2, k=NUM_FEATURES)
    test.fit(X, y)
    cols = test.get_support(indices=True)
    selected_features = training_data.iloc[:, cols+3]

    return selected_features, training_data.iloc[:, 2:3], training_data.iloc[:, 0:2]


def get_training_data(playlist_ids):
    track_names = get_track_names(playlist_ids)
    track_features = get_track_features(track_names)
    combined_data = combine_track_data(track_names, track_features)
    normalized_training_data = normalize_features(combined_data)
    X, y, tags = select_features(normalized_training_data)

    return X, y, tags


def main():
    X_train, y_train, tags_train = get_training_data(TRAINING_PLAYLIST_IDS)


main()
