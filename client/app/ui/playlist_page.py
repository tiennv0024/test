from PySide2.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.db.repositories import LibraryRepository
from app.services.playlist_service import PlaylistService


class PlaylistPage(QWidget):
    def __init__(self, playlist_service: PlaylistService, library_repository: LibraryRepository) -> None:
        super().__init__()
        self.playlist_service = playlist_service
        self.library_repository = library_repository

        self.playlists = QComboBox()
        self.tracks = QListWidget()
        self.local_tracks = QComboBox()
        self.create_button = QPushButton("New")
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        self.up_button = QPushButton("Up")
        self.down_button = QPushButton("Down")
        self.shuffle_button = QPushButton("Shuffle")
        self.loop_button = QPushButton("Loop All")

        top = QHBoxLayout()
        top.addWidget(self.playlists, 1)
        top.addWidget(self.create_button)

        add_row = QHBoxLayout()
        add_row.addWidget(self.local_tracks, 1)
        add_row.addWidget(self.add_button)

        actions = QHBoxLayout()
        for button in [self.remove_button, self.up_button, self.down_button, self.shuffle_button, self.loop_button]:
            actions.addWidget(button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(add_row)
        layout.addWidget(self.tracks, 1)
        layout.addLayout(actions)

        self.create_button.clicked.connect(self.create_playlist)
        self.add_button.clicked.connect(self.add_track)
        self.remove_button.clicked.connect(self.remove_track)
        self.up_button.clicked.connect(lambda: self.move_selected(-1))
        self.down_button.clicked.connect(lambda: self.move_selected(1))
        self.playlists.currentIndexChanged.connect(self.refresh_tracks)
        self.refresh()

    def refresh(self) -> None:
        current_id = self.current_playlist_id()
        self.playlists.clear()
        for playlist in self.playlist_service.list_playlists():
            self.playlists.addItem(playlist.name, playlist.id)
        if current_id:
            index = self.playlists.findData(current_id)
            if index >= 0:
                self.playlists.setCurrentIndex(index)
        self.refresh_local_tracks()
        self.refresh_tracks()

    def refresh_local_tracks(self) -> None:
        self.local_tracks.clear()
        for track in self.library_repository.list_tracks():
            self.local_tracks.addItem(track.title, track.id)

    def refresh_tracks(self) -> None:
        self.tracks.clear()
        playlist_id = self.current_playlist_id()
        if not playlist_id:
            return
        for track in self.playlist_service.tracks(playlist_id):
            self.tracks.addItem(f"{track.title} - {track.artist or 'Unknown artist'}")

    def current_playlist_id(self) -> int | None:
        value = self.playlists.currentData()
        return int(value) if value else None

    def create_playlist(self) -> None:
        name, ok = QInputDialog.getText(self, "New Playlist", "Name")
        if ok and name.strip():
            playlist = self.playlist_service.create(name)
            self.refresh()
            self.playlists.setCurrentIndex(self.playlists.findData(playlist.id))

    def add_track(self) -> None:
        playlist_id = self.current_playlist_id()
        track_id = self.local_tracks.currentData()
        if playlist_id and track_id:
            self.playlist_service.add_track(playlist_id, int(track_id))
            self.refresh_tracks()

    def remove_track(self) -> None:
        playlist_id = self.current_playlist_id()
        row = self.tracks.currentRow()
        if not playlist_id or row < 0:
            return
        track_ids = [track.id for track in self.playlist_service.tracks(playlist_id)]
        if row < len(track_ids):
            self.playlist_service.remove_track(playlist_id, int(track_ids[row]))
            self.refresh_tracks()

    def move_selected(self, direction: int) -> None:
        playlist_id = self.current_playlist_id()
        row = self.tracks.currentRow()
        if not playlist_id or row < 0:
            return
        track_ids = [track.id for track in self.playlist_service.tracks(playlist_id)]
        new_row = row + direction
        if new_row < 0 or new_row >= len(track_ids):
            return
        track_ids[row], track_ids[new_row] = track_ids[new_row], track_ids[row]
        self.playlist_service.reorder(playlist_id, [int(track_id) for track_id in track_ids if track_id is not None])
        self.refresh_tracks()
        self.tracks.setCurrentRow(new_row)
