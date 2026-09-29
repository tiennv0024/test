import os
from pathlib import Path

import requests


class ApiError(RuntimeError):
    pass


class ApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 15.0) -> None:
        self.base_url = (base_url or os.environ.get("EUREKA_SERVER_URL") or "http://localhost:8000").rstrip("/")
        self.timeout = timeout

    def list_tracks(self, page: int = 1, page_size: int = 50, q: str | None = None) -> dict:
        response = requests.get(
            f"{self.base_url}/api/v1/tracks",
            params={"page": page, "page_size": page_size, "q": q},
            timeout=self.timeout,
        )
        return self._json(response)

    def download_track(self, track_id: int, target_path: Path) -> Path:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = target_path.with_suffix(target_path.suffix + ".part")
        response = requests.get(
            f"{self.base_url}/api/v1/tracks/{track_id}/download",
            stream=True,
            timeout=self.timeout,
        )
        if response.status_code != 200:
            raise ApiError(response.text)
        try:
            with temp_path.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        handle.write(chunk)
            temp_path.replace(target_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
        return target_path

    def upload_track(
        self,
        file_path: Path,
        *,
        title: str,
        artist: str | None = None,
        album: str | None = None,
        genre: str | None = None,
    ) -> dict:
        with file_path.open("rb") as handle:
            response = requests.post(
                f"{self.base_url}/api/v1/tracks",
                data={"title": title, "artist": artist or "", "album": album or "", "genre": genre or ""},
                files={"file": (file_path.name, handle, "application/octet-stream")},
                timeout=self.timeout,
            )
        return self._json(response)

    @staticmethod
    def _json(response: requests.Response) -> dict:
        if response.status_code >= 400:
            raise ApiError(response.text)
        return response.json()
