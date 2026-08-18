from typing import TypeVar

T = TypeVar("T")


def unwrap[T](value: T | None) -> T:
    if value is None:
        raise RuntimeError("Spotify-API returned no data")
    return value
