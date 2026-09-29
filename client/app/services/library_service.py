import os
from pathlib import Path

from app.api.api_client import ApiClient
from app.db.database import app_data_dir
from app.db.repositories import LibraryRepository
from app.models.track import Track


class LibraryService:
    def __init__(self, repository: LibraryRepository, api_client: ApiClient | None = None) -> None:
        self.repository = repository
        self.api_client = api_client or ApiClient()

    def register_downloaded_track(self, server_track: dict, file_path: Path) -> Track:
        return self.repository.upsert_local_track(
            server_track_id=server_track["id"],
            title=server_track["title"],
            artist=server_track.get("artist"),
            album=server_track.get("album"),
            genre=server_track.get("genre"),
            file_path=str(file_path),
            duration_ms=server_track.get("duration_ms"),
        )

    def target_download_path(self, server_track: dict) -> Path:
        safe_name = f'{server_track["id"]}_{server_track["title"]}'.strip().replace(os.sep, "_")
        return app_data_dir() / "tracks" / f"{safe_name}.mp3"
