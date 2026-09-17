from playlistr.spotify import add_tracks, get_all_songs
from playlistr.tui import select_artist, select_playlist, select_songs


def main() -> None:
    all_songs = get_all_songs()
    try:
        while True:
            artist = select_artist(all_songs)
            if not artist:
                continue
            songs = select_songs(artist, all_songs)
            if not songs:
                continue
            playlist = select_playlist()
            if playlist is None:
                continue
            add_tracks(playlist, songs)
    except KeyboardInterrupt:
        print("\nBis bald!")
