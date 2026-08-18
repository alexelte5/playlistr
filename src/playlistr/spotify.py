import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyPKCE

from playlistr.helper import unwrap

_sp: spotipy.Spotify | None = None

CACHE_PATH = Path("song_cache.json")
CACHE_MAX_AGE_SECONDS = 60 * 60 * 1


def get_client() -> spotipy.Spotify:
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(
            auth_manager=SpotifyPKCE(
                client_id="568486f0df864f1c95d2f0648c21c9c2",
                redirect_uri="http://127.0.0.1:8989/login",
                scope="user-top-read user-library-read playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public",
            )
        )
    return _sp


def get_own_playlists():
    me = unwrap(get_client().current_user())
    my_id = me["id"]

    offset = 0
    limit = 50
    playlists = []

    while True:
        results = unwrap(get_client().current_user_playlists(limit, offset))
        items = results["items"]
        if not items:
            break
        for playlist in items:
            if playlist["owner"]["id"] == my_id:
                playlists.append(playlist)
        offset += limit
    return playlists


def get_liked_songs():
    tracks = []
    offset = 0
    limit = 50

    while True:
        results = unwrap(
            get_client().current_user_saved_tracks(limit=limit, offset=offset)
        )
        items = results["items"]
        if not items:
            break
        for item in items:
            track = item.get("track")
            if track:
                tracks.append(track)
        offset += limit

    return tracks


def get_playlist_tracks(playlist_id: str):
    tracks = []
    offset = 0
    limit = 100

    while True:
        results = unwrap(
            get_client().playlist_items(playlist_id, limit=limit, offset=offset)
        )
        items = results["items"]
        if not items:
            break
        for item in items:
            track = item.get("track")
            if track:
                tracks.append(track)
        offset += limit

    return tracks


def get_all_own_playlist_tracks():
    all_tracks = []

    for playlist in get_own_playlists():
        all_tracks.extend(get_playlist_tracks(playlist["id"]))

    return all_tracks


def songs_by_artist(artist_ids: list[str], all_songs: list):
    artist_id_set = set(artist_ids)
    seen_ids = set()
    matches = []
    for track in all_songs:
        if track["id"] in seen_ids:
            continue
        track_artist_ids = {a["id"] for a in track["artists"]}
        if track_artist_ids & artist_id_set:
            matches.append(track)
            seen_ids.add(track["id"])

    return matches


def get_all_songs():
    try:
        if CACHE_PATH.exists():
            cache = json.loads(CACHE_PATH.read_text())
            if time.time() - cache["timestamp"] < CACHE_MAX_AGE_SECONDS:
                return cache["songs"]
    except json.JSONDecodeError as e:
        print(e)

    all_songs = get_liked_songs() + get_all_own_playlist_tracks()

    CACHE_PATH.write_text(json.dumps({"timestamp": time.time(), "songs": all_songs}))

    return all_songs


def get_artist_counts(all_songs: list):
    seen_ids = set()
    names = {}
    counts = Counter()
    for track in all_songs:
        if track["id"] in seen_ids:
            continue
        seen_ids.add(track["id"])
        for artist in track["artists"]:
            artist_id = artist["id"]
            names[artist_id] = artist["name"]
            counts[artist_id] += 1

    by_name = defaultdict(list)
    for artist_id in counts:
        by_name[names[artist_id]].append(artist_id)

    result = [
        (ids, name, sum(counts[aid] for aid in ids)) for name, ids in by_name.items()
    ]

    return sorted(result, key=lambda entry: entry[2], reverse=True)


def get_all_playlists():
    me = unwrap(get_client().current_user())
    my_id = me["id"]

    offset = 0
    limit = 50
    playlists = []
    while True:
        results = unwrap(get_client().current_user_playlists(limit, offset))
        items = results["items"]
        if not items:
            break
        for playlist in items:
            if playlist["owner"]["id"] == my_id:
                playlists.append(playlist)
        offset += limit
    return playlists


def get_playlist(name: str):
    for playlist in get_own_playlists():
        if playlist["name"] == name:
            return playlist["id"]
    return None


def get_or_create_playlist(name: str):
    playlist_id = get_playlist(name)
    if playlist_id:
        return playlist_id

    new_playlist = unwrap(
        get_client().current_user_playlist_create(
            name=name,
            public=False,
            description="Automatisch erstellt von playlistr",
        )
    )
    return new_playlist["id"]


def add_tracks(playlist_id: str, tracks: list[dict]):
    existing_ids = {t["id"] for t in get_playlist_tracks(playlist_id)}
    new_track_uris = [t["uri"] for t in tracks if t["id"] not in existing_ids]

    if not new_track_uris:
        return

    for i in range(0, len(new_track_uris), 100):
        batch = new_track_uris[i : i + 100]
        get_client().playlist_add_items(playlist_id, batch)

    return len(new_track_uris)
