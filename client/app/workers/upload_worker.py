from pathlib import Path

from PySide2.QtCore import QObject, Signal, Slot

from app.api.api_client import ApiClient


class UploadWorker(QObject):
    succeeded = Signal(dict)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        api_client: ApiClient,
        file_path: Path,
        title: str,
        artist: str | None,
        album: str | None,
        genre: str | None,
    ) -> None:
        super().__init__()
        self.api_client = api_client
        self.file_path = file_path
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(
                self.api_client.upload_track(
                    self.file_path,
                    title=self.title,
                    artist=self.artist,
                    album=self.album,
                    genre=self.genre,
                )
            )
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()
