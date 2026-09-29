from app.database import SessionLocal
from app.repositories.track_repository import TrackRepository
from app.schemas.track import TrackCreate


def test_download_not_found(client):
    response = client.get("/api/v1/tracks/9999/download")

    assert response.status_code == 404


def test_download_missing_audio_file(client, tmp_path):
    missing = tmp_path / "missing.mp3"
    with SessionLocal() as db:
        track = TrackRepository(db).create(
            TrackCreate(title="Missing", file_path=str(missing))
        )

    response = client.get(f"/api/v1/tracks/{track.id}/download")

    assert response.status_code == 404


def test_download_valid_file(client, tmp_path):
    audio = tmp_path / "track.mp3"
    audio.write_bytes(b"audio bytes")
    with SessionLocal() as db:
        track = TrackRepository(db).create(
            TrackCreate(title="Downloadable", file_path=str(audio), file_size=audio.stat().st_size)
        )

    response = client.get(f"/api/v1/tracks/{track.id}/download")

    assert response.status_code == 200
    assert response.content == b"audio bytes"
