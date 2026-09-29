from PySide2.QtWidgets import QListWidget, QMainWindow, QMessageBox, QSplitter, QStackedWidget, QVBoxLayout, QWidget

from app.api.api_client import ApiClient
from app.db.database import get_connection, init_db
from app.db.repositories import LibraryRepository, PlaylistRepository
from app.services.library_service import LibraryService
from app.services.playback_service import PlaybackService
from app.services.playlist_service import PlaylistService
from app.ui.catalog_page import CatalogPage
from app.ui.library_page import LibraryPage
from app.ui.player_widget import PlayerWidget
from app.ui.playlist_page import PlaylistPage
from app.ui.upload_page import UploadPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Eureka Music")
        self.resize(1100, 720)

        self.conn = get_connection()
        init_db(self.conn)
        self.api_client = ApiClient()
        self.library_repository = LibraryRepository(self.conn)
        self.playlist_repository = PlaylistRepository(self.conn)
        self.library_service = LibraryService(self.library_repository, self.api_client)
        self.playlist_service = PlaylistService(self.playlist_repository)
        self.playback_service = PlaybackService()

        self.navigation = QListWidget()
        self.navigation.addItems(["Catalog", "Library", "Playlists", "Upload"])
        self.navigation.setFixedWidth(150)

        self.stack = QStackedWidget()
        self.catalog_page = CatalogPage(self.api_client, self.library_service)
        self.library_page = LibraryPage(self.library_repository)
        self.playlist_page = PlaylistPage(self.playlist_service, self.library_repository)
        self.upload_page = UploadPage(self.api_client)

        for page in [self.catalog_page, self.library_page, self.playlist_page, self.upload_page]:
            self.stack.addWidget(page)

        splitter = QSplitter()
        splitter.addWidget(self.navigation)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)

        self.player = PlayerWidget(self.playback_service)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.player)
        self.setCentralWidget(root)

        self.navigation.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.navigation.setCurrentRow(0)
        self.catalog_page.downloaded.connect(self.refresh_local_views)
        self.upload_page.uploaded.connect(self.catalog_page.reload)
        self.library_page.play_requested.connect(self.play_track)

    def refresh_local_views(self) -> None:
        self.library_page.refresh()
        self.playlist_page.refresh()

    def play_track(self, track) -> None:
        try:
            self.player.play_track(track)
        except Exception as exc:
            QMessageBox.warning(self, "Eureka Music", str(exc))
