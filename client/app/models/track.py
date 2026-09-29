from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    id: int | None
    title: str
    artist: str | None = None
    album: str | None = None
    genre: str | None = None
    server_track_id: int | None = None
    file_path: str | None = None
    duration_ms: int | None = None
    file_size: int | None = None


@dataclass(frozen=True)
class Playlist:
    id: int
    name: str
