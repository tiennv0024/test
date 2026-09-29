from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QStyle, QWidget

from app.models.track import Track
from app.services.playback_service import PlaybackService


class PlayerWidget(QWidget):
    def __init__(self, playback_service: PlaybackService) -> None:
        super().__init__()
        self.playback_service = playback_service
        self.current_track: Track | None = None
        self.duration_ms = 0

        self.now_playing = QLabel("Nothing playing")
        self.now_playing.setObjectName("MutedLabel")
        self.pause_button = QPushButton("Pause/Continue")
        self.stop_button = QPushButton("Stop")
        self.pause_button.setObjectName("PrimaryButton")
        self.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.seek = QSlider(Qt.Horizontal)
        self.seek.setRange(0, 0)
        self.elapsed = QLabel("0:00")
        self.elapsed.setObjectName("MutedLabel")
        self.duration = QLabel("0:00")
        self.duration.setObjectName("MutedLabel")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        layout.addWidget(self.now_playing, 2)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.elapsed)
        layout.addWidget(self.seek, 3)
        layout.addWidget(self.duration)

        self.pause_button.clicked.connect(self.playback_service.pause_or_resume)
        self.stop_button.clicked.connect(self.playback_service.stop)
        self.seek.sliderMoved.connect(self.playback_service.seek)

        player = self.playback_service.player
        if player is not None:
            player.positionChanged.connect(self.update_position)
            player.durationChanged.connect(self.update_duration)

    def play_track(self, track: Track) -> None:
        if not track.file_path:
            return
        self.current_track = track
        self.now_playing.setText(f"{track.title} - {track.artist or 'Unknown artist'}")
        self.playback_service.play_file(track.file_path)

    def update_position(self, position_ms: int) -> None:
        self.seek.setValue(position_ms)
        self.elapsed.setText(self._format_time(position_ms))

    def update_duration(self, duration_ms: int) -> None:
        self.duration_ms = duration_ms
        self.seek.setMaximum(duration_ms)
        self.duration.setText(self._format_time(duration_ms))

    @staticmethod
    def _format_time(value_ms: int) -> str:
        seconds = max(0, int(value_ms) // 1000)
        return f"{seconds // 60}:{seconds % 60:02d}"
