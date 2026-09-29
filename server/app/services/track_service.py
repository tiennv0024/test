import logging
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from mutagen import File as MutagenFile
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models.track import Track
from app.repositories.track_repository import TrackRepository
from app.schemas.track import TrackCreate

logger = logging.getLogger(__name__)


class InvalidAudioFileError(ValueError):
    pass


class TrackService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.repository = TrackRepository(db)
        self.settings = settings or get_settings()

    def list_tracks(self, page: int, page_size: int, q: str | None = None) -> tuple[list[Track], int]:
        return self.repository.list_tracks(page=page, page_size=page_size, q=q)

    def get_track(self, track_id: int) -> Track | None:
        return self.repository.get(track_id)

    def get_download_path(self, track_id: int) -> Path | None:
        track = self.repository.get(track_id)
        if track is None:
            return None
        path = Path(track.file_path)
        if not path.exists() or not path.is_file():
            logger.warning("Track %s references missing file %s", track_id, path)
            return None
        return path

    def create_uploaded_track(
        self,
        upload: UploadFile,
        title: str,
        artist: str | None,
        album: str | None,
        genre: str | None,
    ) -> Track:
        extension = Path(upload.filename or "").suffix.lower()
        if extension not in self.settings.allowed_audio_extensions:
            raise InvalidAudioFileError("Unsupported audio file type")

        self.settings.audio_storage_path.mkdir(parents=True, exist_ok=True)
        final_name = f"{uuid.uuid4().hex}{extension}"
        temp_path = self.settings.audio_storage_path / f".{final_name}.part"
        final_path = self.settings.audio_storage_path / final_name

        try:
            with temp_path.open("wb") as output:
                shutil.copyfileobj(upload.file, output)
            if temp_path.stat().st_size == 0:
                raise InvalidAudioFileError("Uploaded file is empty")
            duration_ms = self._duration_ms(temp_path)
            temp_path.replace(final_path)
            track = self.repository.create(
                TrackCreate(
                    title=title,
                    artist=artist,
                    album=album,
                    genre=genre,
                    file_path=str(final_path),
                    duration_ms=duration_ms,
                    file_size=final_path.stat().st_size,
                )
            )
            logger.info("Uploaded track %s to %s", track.id, final_path)
            return track
        except Exception:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            if final_path.exists():
                final_path.unlink(missing_ok=True)
            logger.exception("Upload failed for %s", upload.filename)
            raise

    @staticmethod
    def _duration_ms(path: Path) -> int | None:
        try:
            audio = MutagenFile(path)
            if audio is None or audio.info is None:
                return None
            return int(audio.info.length * 1000)
        except Exception:
            logger.warning("Unable to parse duration for %s", path, exc_info=True)
            return None
