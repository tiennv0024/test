from PySide2.QtCore import Signal
from PySide2.QtWidgets import QHeaderView, QHBoxLayout, QLabel, QPushButton, QStyle, QTableView, QVBoxLayout, QWidget

from app.db.repositories import LibraryRepository
from app.models.track import Track
from app.ui.table_models import TrackTableModel


class LibraryPage(QWidget):
    play_requested = Signal(object)

    def __init__(self, repository: LibraryRepository) -> None:
        super().__init__()
        self.repository = repository
        self.title = QLabel("Local Library")
        self.title.setObjectName("PageTitle")
        self.status = QLabel("")
        self.status.setObjectName("MutedLabel")
        self.table = QTableView()
        self.model = TrackTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.play_button = QPushButton("Play")
        self.refresh_button = QPushButton("Refresh")
        self.play_button.setObjectName("PrimaryButton")
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))

        header = QHBoxLayout()
        header.addWidget(self.title)
        header.addStretch(1)
        header.addWidget(self.status)

        actions = QHBoxLayout()
        actions.addWidget(self.play_button)
        actions.addWidget(self.refresh_button)
        actions.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addLayout(header)
        layout.addLayout(actions)
        layout.addWidget(self.table, 1)

        self.play_button.clicked.connect(self.play_selected)
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        self.tracks = self.repository.list_tracks()
        self.model.set_tracks([track.__dict__ for track in self.tracks])
        self.status.setText(f"{len(self.tracks)} downloaded tracks")

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
