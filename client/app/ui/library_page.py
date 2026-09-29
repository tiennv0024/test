from PySide2.QtCore import Signal
from PySide2.QtWidgets import QHBoxLayout, QPushButton, QTableView, QVBoxLayout, QWidget

from app.db.repositories import LibraryRepository
from app.models.track import Track
from app.ui.table_models import TrackTableModel


class LibraryPage(QWidget):
    play_requested = Signal(object)

    def __init__(self, repository: LibraryRepository) -> None:
        super().__init__()
        self.repository = repository
        self.table = QTableView()
        self.model = TrackTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.play_button = QPushButton("Play")
        self.refresh_button = QPushButton("Refresh")

        actions = QHBoxLayout()
        actions.addWidget(self.play_button)
        actions.addWidget(self.refresh_button)
        actions.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table, 1)

        self.play_button.clicked.connect(self.play_selected)
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        self.tracks = self.repository.list_tracks()
        self.model.set_tracks([track.__dict__ for track in self.tracks])

    def selected_track(self) -> Track | None:
        index = self.table.currentIndex()
        if not index.isValid() or not hasattr(self, "tracks"):
            return None
        if 0 <= index.row() < len(self.tracks):
            return self.tracks[index.row()]
        return None

    def play_selected(self) -> None:
        track = self.selected_track()
        if track:
            self.play_requested.emit(track)
