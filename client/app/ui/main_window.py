from PySide2.QtWidgets import QListWidget, QMainWindow, QMessageBox, QSplitter, QStackedWidget, QVBoxLayout, QWidget

from app.api.api_client import ApiClient
from app.db.database import get_connection, init_db
from app.db.repositories import LibraryRepository, PlaylistRepository
from app.services.library_service import LibraryService
from app.services.playback_service import LOOP_OFF, PlaybackQueue, PlaybackService
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
        self.playback_queue = PlaybackQueue(loop_mode=LOOP_OFF)
        self.queue_tracks = {}

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
        self.playlist_page.play_requested.connect(self.play_playlist)
        if self.playback_service.player is not None:
            self.playback_service.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def refresh_local_views(self) -> None:
        self.library_page.refresh()
        self.playlist_page.refresh()

    def play_track(self, track) -> None:
        self._play_track(track, reset_queue=True)

    def _play_track(self, track, reset_queue: bool) -> None:
        try:
            if reset_queue and track.id is not None:
                self.queue_tracks = {track.id: track}
                self.playback_queue.set_tracks([track.id])
            self.player.play_track(track)
        except Exception as exc:
            QMessageBox.warning(self, "Eureka Music", str(exc))

    def play_playlist(self, tracks, start_index: int, shuffle_enabled: bool, loop_mode: str) -> None:
        track_ids = [track.id for track in tracks if track.id is not None]
        self.queue_tracks = {track.id: track for track in tracks if track.id is not None}
        self.playback_queue.set_tracks(track_ids, start_index)
        self.playback_queue.loop_mode = loop_mode
        self.playback_queue.set_shuffle(shuffle_enabled)
        current_id = self.playback_queue.current()
        if current_id is not None:
            self._play_track(self.queue_tracks[current_id], reset_queue=False)

    def on_media_status_changed(self, status) -> None:
        player = self.playback_service.player
        if player is None or status != player.EndOfMedia:
            return
        next_id = self.playback_queue.next()
        if next_id is None:
            return
        track = self.queue_tracks.get(next_id)
        if track is not None:
            self._play_track(track, reset_queue=False)
