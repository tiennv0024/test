from pathlib import Path

from PySide2.QtCore import QThread, QTimer, Signal
from PySide2.QtWidgets import (
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStyle,
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

        self.title = QLabel("Server Catalog")
        self.title.setObjectName("PageTitle")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search catalog")
        self.search.setClearButtonEnabled(True)
        self.status = QLabel("")
        self.status.setObjectName("MutedLabel")
        self.page_status = QLabel("")
        self.page_status.setObjectName("MutedLabel")
        self.table = QTableView()
        self.model = TrackTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.download_button = QPushButton("Download")
        self.refresh_button = QPushButton("Refresh")
        self.download_button.setObjectName("PrimaryButton")
        self.previous_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        self.next_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.download_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))

        header = QHBoxLayout()
        header.addWidget(self.title)
        header.addStretch(1)
        header.addWidget(self.status)

        top = QHBoxLayout()
        top.addWidget(self.search, 1)
        top.addWidget(self.refresh_button)
        top.addWidget(self.download_button)

        pager = QHBoxLayout()
        pager.addWidget(self.previous_button)
        pager.addWidget(self.next_button)
        pager.addWidget(self.page_status, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addLayout(header)
        layout.addLayout(top)
        layout.addWidget(self.table, 1)
        layout.addLayout(pager)

        self.search_timer = QTimer(self)
        self.search_timer.setInterval(300)
        self.search_timer.setSingleShot(True)
        self.search.textChanged.connect(self.search_changed)
        self.search_timer.timeout.connect(self.reload)
        self.refresh_button.clicked.connect(self.reload)
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.download_button.clicked.connect(self.download_selected)

        self.reload()

    def search_changed(self) -> None:
        self.page = 1
        self.search_timer.start()

    def reload(self) -> None:
        self.status.setText("Loading...")
        self.refresh_button.setEnabled(False)
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
        self.status.setText("Ready")
        self.page_status.setText(f"Page {self.page} / {max(1, ((self.total - 1) // self.page_size) + 1)} - {self.total} tracks")
        self.previous_button.setEnabled(self.page > 1)
        self.next_button.setEnabled(self.page * self.page_size < self.total)
        self.refresh_button.setEnabled(True)

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
        self.refresh_button.setEnabled(True)
        QMessageBox.warning(self, "Eureka Music", message)

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self.threads:
            self.threads.remove(thread)
