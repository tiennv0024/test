from app.db.repositories import PlaylistRepository
from app.models.track import Playlist, Track


class PlaylistService:
    def __init__(self, repository: PlaylistRepository) -> None:
        self.repository = repository

    def create(self, name: str) -> Playlist:
        if not name.strip():
            raise ValueError("Playlist name is required")
        return self.repository.create_playlist(name.strip())

    def list_playlists(self) -> list[Playlist]:
        return self.repository.list_playlists()

    def add_track(self, playlist_id: int, track_id: int) -> None:
        self.repository.add_track(playlist_id, track_id)

    def remove_track(self, playlist_id: int, track_id: int) -> None:
        self.repository.remove_track(playlist_id, track_id)

    def reorder(self, playlist_id: int, track_ids: list[int]) -> None:
        self.repository.reorder(playlist_id, track_ids)

    def tracks(self, playlist_id: int) -> list[Track]:
        return self.repository.playlist_tracks(playlist_id)
