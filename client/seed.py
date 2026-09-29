import argparse
import csv
import logging
import shutil
import sys
from pathlib import Path

from mutagen import File as MutagenFile

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import app_data_dir, get_connection, init_db  # noqa: E402
from app.db.repositories import LibraryRepository  # noqa: E402

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
        logger.warning("Unable to parse duration for %s", path, exc_info=True)
        return None


def seed(root: Path, limit: int | None = None) -> int:
    metadata = root / "fma_metadata" / "tracks.csv"
    if not metadata.exists():
        raise FileNotFoundError(f"Missing metadata file: {metadata}")

    destination_dir = app_data_dir() / "tracks"
    count = 0
    conn = get_connection()
    init_db(conn)
    repo = LibraryRepository(conn)
    try:
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
                target = destination_dir / audio_path.name
                temp = target.with_suffix(target.suffix + ".part")
                shutil.copyfile(audio_path, temp)
                temp.replace(target)
                repo.upsert_local_track(
                    server_track_id=None,
                    title=data.get(("track", "title")) or f"Track {track_id}",
                    artist=data.get(("artist", "name")) or None,
                    album=data.get(("album", "title")) or None,
                    genre=data.get(("track", "genre_top")) or None,
                    file_path=str(target),
                    duration_ms=duration_ms(target),
                )
                count += 1
                if limit is not None and count >= limit:
                    break
    finally:
        conn.close()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Eureka Music client library from FMA Small")
    parser.add_argument("fma_root", type=Path)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    logger.info("Seeded %s local tracks", seed(args.fma_root, args.limit))


if __name__ == "__main__":
    main()
