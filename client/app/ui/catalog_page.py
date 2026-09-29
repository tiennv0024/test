from pathlib import Path

from PySide2.QtCore import QThread, QTimer, Signal
from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.api.api_client import ApiClient
from app.services.library_service import LibraryService
from app.ui.table_models import TrackTableModel
from app.workers.catalog_worker import CatalogWorker
from app.workers.download_worker import DownloadWorker


class CatalogPage(QWidget):
    downloaded = Signal()

    def __init__(self, api_client: ApiClient, library_service: LibraryService) -> None:
        super().__init__()
        self.api_client = api_client
        self.library_service = library_service
        self.page = 1
        self.page_size = 50
        self.total = 0
        self.threads: list[QThread] = []

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search catalog")
        self.status = QLabel("")
        self.table = QTableView()
        self.model = TrackTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSortingEnabled(False)

        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.download_button = QPushButton("Download")
        self.refresh_button = QPushButton("Refresh")

        top = QHBoxLayout()
        top.addWidget(self.search, 1)
        top.addWidget(self.refresh_button)
        top.addWidget(self.download_button)

        pager = QHBoxLayout()
        pager.addWidget(self.previous_button)
        pager.addWidget(self.next_button)
        pager.addWidget(self.status, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table, 1)
        layout.addLayout(pager)

        self.search_timer = QTimer(self)
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search.textChanged.connect(lambda: self.search_timer.start())
        self.search_timer.timeout.connect(self.reload)
        self.refresh_button.clicked.connect(self.reload)
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.download_button.clicked.connect(self.download_selected)

        self.reload()

    def reload(self) -> None:
        self.status.setText("Loading...")
        thread = QThread(self)
        worker = CatalogWorker(self.api_client, self.page, self.page_size, self.search.text().strip() or None)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self.apply_catalog)
        worker.failed.connect(self.show_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))
        self.threads.append(thread)
        thread.start()

    def apply_catalog(self, payload: dict) -> None:
        self.total = int(payload.get("total", 0))
        self.model.set_tracks(payload.get("items", []))
        self.status.setText(f"Page {self.page} - {self.total} tracks")

    def previous_page(self) -> None:
        if self.page > 1:
            self.page -= 1
            self.reload()

    def next_page(self) -> None:
        if self.page * self.page_size < self.total:
            self.page += 1
            self.reload()

    def download_selected(self) -> None:
        index = self.table.currentIndex()
        track = self.model.track_at(index.row())
        if not track:
            return
        target = self.library_service.target_download_path(track)
        thread = QThread(self)
        worker = DownloadWorker(self.api_client, track, Path(target))
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self.register_download)
        worker.failed.connect(self.show_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))
        self.threads.append(thread)
        self.status.setText("Downloading...")
        thread.start()

    def register_download(self, server_track: dict, path: str) -> None:
        self.library_service.register_downloaded_track(server_track, Path(path))
        self.status.setText("Download complete")
        self.downloaded.emit()

    def show_error(self, message: str) -> None:
        self.status.setText("Error")
        QMessageBox.warning(self, "Eureka Music", message)

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self.threads:
            self.threads.remove(thread)
