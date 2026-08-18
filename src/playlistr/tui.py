import questionary

from playlistr.spotify import (
    get_all_playlists,
    get_artist_counts,
    get_or_create_playlist,
    songs_by_artist,
)


def select_artist(all_songs):
    artist_counts = get_artist_counts(all_songs)
    name_to_ids = {name: ids for ids, name, _ in artist_counts}

    name = questionary.autocomplete(
        "Welcher Künstler?",
        choices=list(name_to_ids),
        ignore_case=True,
        meta_information={name: f"{count} Songs" for _, name, count in artist_counts},
    ).ask()

    return name_to_ids.get(name, [])


def select_playlist():
    playlists = get_all_playlists()
    choices = [questionary.Choice(title=p["name"], value=p["id"]) for p in playlists]
    choices.append(
        questionary.Choice(title="+ Neue Playlist erstellen", value="__new__")
    )
    selection = questionary.select("Welche Playlist?", choices).ask()
    if selection is None:
        return None

    if selection == "__new__":
        playlist_name = questionary.text("Name der neuen Playlist:").ask()
        if playlist_name is None:
            return None
        return get_or_create_playlist(playlist_name)

    return selection


def select_songs(artist_ids, all_songs: list):
    tracks = songs_by_artist(artist_ids, all_songs)
    if not tracks:
        print("Keine Songs für diesen Artist gefunden")
        return
    choices = [questionary.Choice(title=t["name"], value=t) for t in tracks]
    songs = questionary.checkbox("Welche Lieder?", choices).ask()
    return songs
