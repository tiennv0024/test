import random
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PySide2.QtCore import QObject, QUrl, Signal
    from PySide2.QtMultimedia import QMediaContent, QMediaPlayer
except ImportError:  # Allows pure logic tests without PySide2 installed.
    QObject = object  # type: ignore[misc, assignment]
    Signal = lambda *args, **kwargs: None  # type: ignore[assignment]
    QMediaPlayer = None  # type: ignore[assignment]
    QMediaContent = None  # type: ignore[assignment]
    QUrl = None  # type: ignore[assignment]


LOOP_OFF = "OFF"
LOOP_ALL = "ALL"
LOOP_ONE = "ONE"


@dataclass
class PlaybackQueue:
    track_ids: list[int] = field(default_factory=list)
    current_index: int = 0
    shuffle_enabled: bool = False
    loop_mode: str = LOOP_OFF

    def current(self) -> int | None:
        if not self.track_ids:
            return None
        return self.track_ids[self.current_index]

    def set_tracks(self, track_ids: list[int], start_index: int = 0) -> None:
        self.track_ids = list(track_ids)
        self.current_index = min(max(start_index, 0), max(len(self.track_ids) - 1, 0))

    def next(self) -> int | None:
        if not self.track_ids:
            return None
        if self.loop_mode == LOOP_ONE:
            return self.current()
        if self.current_index + 1 < len(self.track_ids):
            self.current_index += 1
            return self.current()
        if self.loop_mode == LOOP_ALL:
            self.current_index = 0
            return self.current()
        return None

    def previous(self) -> int | None:
        if not self.track_ids:
            return None
        if self.current_index > 0:
            self.current_index -= 1
        elif self.loop_mode == LOOP_ALL:
            self.current_index = len(self.track_ids) - 1
        return self.current()

    def set_shuffle(self, enabled: bool) -> None:
        current = self.current()
        self.shuffle_enabled = enabled
        if enabled:
            random.shuffle(self.track_ids)
            if current in self.track_ids:
                self.current_index = self.track_ids.index(current)


class PlaybackService(QObject):
    track_changed = Signal(str) if QMediaPlayer else None

    def __init__(self) -> None:
        super().__init__()
        self.player = QMediaPlayer() if QMediaPlayer else None

    def play_file(self, path: str) -> None:
        if self.player is None or QUrl is None or QMediaContent is None:
            raise RuntimeError("PySide2 QtMultimedia is not available")
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(str(Path(path).resolve()))))
        self.player.play()

    def pause_or_resume(self) -> None:
        if self.player is None:
            return
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop(self) -> None:
        if self.player is not None:
            self.player.stop()

    def seek(self, position_ms: int) -> None:
        if self.player is not None:
            self.player.setPosition(position_ms)
