from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt


class TrackTableModel(QAbstractTableModel):
    headers = ["Title", "Artist", "Album", "Genre"]

    def __init__(self, tracks: list[dict] | None = None) -> None:
        super().__init__()
        self.tracks = tracks or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        track = self.tracks[index.row()]
        key = ["title", "artist", "album", "genre"][index.column()]
        return track.get(key) or ""

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def set_tracks(self, tracks: list[dict]) -> None:
        self.beginResetModel()
        self.tracks = tracks
        self.endResetModel()

    def track_at(self, row: int) -> dict | None:
        if 0 <= row < len(self.tracks):
            return self.tracks[row]
        return None
