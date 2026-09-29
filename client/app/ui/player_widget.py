from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget

from app.models.track import Track
from app.services.playback_service import PlaybackService


class PlayerWidget(QWidget):
    def __init__(self, playback_service: PlaybackService) -> None:
        super().__init__()
        self.playback_service = playback_service
        self.current_track: Track | None = None

        self.now_playing = QLabel("Nothing playing")
        self.pause_button = QPushButton("Pause/Continue")
        self.stop_button = QPushButton("Stop")
        self.seek = QSlider(Qt.Horizontal)
        self.seek.setRange(0, 0)

        layout = QHBoxLayout(self)
        layout.addWidget(self.now_playing, 2)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.seek, 3)

        self.pause_button.clicked.connect(self.playback_service.pause_or_resume)
        self.stop_button.clicked.connect(self.playback_service.stop)
        self.seek.sliderMoved.connect(self.playback_service.seek)

        player = self.playback_service.player
        if player is not None:
            player.positionChanged.connect(self.seek.setValue)
            player.durationChanged.connect(self.seek.setMaximum)

    def play_track(self, track: Track) -> None:
        if not track.file_path:
            return
        self.current_track = track
        self.now_playing.setText(f"{track.title} - {track.artist or 'Unknown artist'}")
        self.playback_service.play_file(track.file_path)
