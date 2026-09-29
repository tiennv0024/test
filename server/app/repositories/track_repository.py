from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.track import Track
from app.schemas.track import TrackCreate


class TrackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_tracks(self, page: int, page_size: int, q: str | None = None) -> tuple[list[Track], int]:
        stmt = self._base_query(q)
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(Track.id).offset((page - 1) * page_size).limit(page_size)
            )
        )
        return items, total

    def get(self, track_id: int) -> Track | None:
        return self.db.get(Track, track_id)

    def get_by_fma_id(self, fma_id: int) -> Track | None:
        return self.db.scalar(select(Track).where(Track.fma_id == fma_id))

    def create(self, data: TrackCreate) -> Track:
        track = Track(**data.model_dump())
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return track

    def upsert_fma(self, data: TrackCreate) -> Track:
        if data.fma_id is not None:
            existing = self.get_by_fma_id(data.fma_id)
            if existing is not None:
                existing.title = data.title
                existing.artist = data.artist
                existing.album = data.album
                existing.genre = data.genre
                existing.tags = data.tags
                existing.file_path = data.file_path
                existing.duration_ms = data.duration_ms
                existing.file_size = data.file_size
                self.db.commit()
                self.db.refresh(existing)
                return existing
        return self.create(data)

    @staticmethod
    def _base_query(q: str | None = None) -> Select[tuple[Track]]:
        stmt = select(Track)
        if q:
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    Track.title.ilike(pattern),
                    Track.artist.ilike(pattern),
                    Track.album.ilike(pattern),
                    Track.genre.ilike(pattern),
                )
            )
        return stmt
