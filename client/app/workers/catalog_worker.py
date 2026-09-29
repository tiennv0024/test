from PySide2.QtCore import QObject, Signal, Slot

from app.api.api_client import ApiClient


class CatalogWorker(QObject):
    succeeded = Signal(dict)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, api_client: ApiClient, page: int, page_size: int, query: str | None) -> None:
        super().__init__()
        self.api_client = api_client
        self.page = page
        self.page_size = page_size
        self.query = query

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(self.api_client.list_tracks(self.page, self.page_size, self.query))
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()
