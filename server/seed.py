import argparse
import csv
import logging
import sys
from pathlib import Path

from mutagen import File as MutagenFile

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal, init_db  # noqa: E402
from app.repositories.track_repository import TrackRepository  # noqa: E402
from app.schemas.track import TrackCreate  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_audio_path(root: Path, track_id: int) -> Path:
    value = f"{track_id:06d}"
    return root / "fma_small" / value[:3] / f"{value}.mp3"


def duration_ms(path: Path) -> int | None:
    try:
        audio = MutagenFile(path)
        if audio is None or audio.info is None:
            return None
        return int(audio.info.length * 1000)
    except Exception:
        logger.warning("Unable to parse metadata from %s", path, exc_info=True)
        return None


def read_fma_tracks(root: Path, limit: int | None = None) -> list[TrackCreate]:
    metadata = root / "fma_metadata" / "tracks.csv"
    if not metadata.exists():
        raise FileNotFoundError(f"Missing metadata file: {metadata}")

    rows: list[TrackCreate] = []
    with metadata.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader)
        subheaders = next(reader)
        next(reader, None)
        columns = [(headers[i], subheaders[i]) for i in range(len(headers))]

        for raw in reader:
            if not raw:
                continue
            try:
                track_id = int(raw[0])
            except ValueError:
                continue
            audio_path = get_audio_path(root, track_id)
            if not audio_path.exists():
                continue
            data = {columns[i]: raw[i] if i < len(raw) else "" for i in range(len(columns))}
            title = data.get(("track", "title")) or f"Track {track_id}"
            artist = data.get(("artist", "name")) or None
            album = data.get(("album", "title")) or None
            genre = data.get(("track", "genre_top")) or None
            tags = data.get(("track", "tags")) or None
            rows.append(
                TrackCreate(
                    fma_id=track_id,
                    title=title,
                    artist=artist,
                    album=album,
                    genre=genre,
                    tags=tags,
                    file_path=str(audio_path.resolve()),
                    duration_ms=duration_ms(audio_path),
                    file_size=audio_path.stat().st_size,
                )
            )
            if limit is not None and len(rows) >= limit:
                break
    return rows


def seed(root: Path, limit: int | None = None) -> int:
    init_db()
    rows = read_fma_tracks(root, limit)
    with SessionLocal() as db:
        repo = TrackRepository(db)
        for row in rows:
            repo.upsert_fma(row)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Eureka Music server from FMA Small")
    parser.add_argument("fma_root", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    count = seed(args.fma_root, args.limit)
    logger.info("Seeded %s tracks", count)


if __name__ == "__main__":
    main()
