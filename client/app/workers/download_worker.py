from pathlib import Path

from PySide2.QtCore import QObject, Signal, Slot

from app.api.api_client import ApiClient


class DownloadWorker(QObject):
    succeeded = Signal(dict, str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, api_client: ApiClient, server_track: dict, target_path: Path) -> None:
        super().__init__()
        self.api_client = api_client
        self.server_track = server_track
        self.target_path = target_path

    @Slot()
    def run(self) -> None:
        try:
            path = self.api_client.download_track(self.server_track["id"], self.target_path)
            self.succeeded.emit(self.server_track, str(path))
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()
