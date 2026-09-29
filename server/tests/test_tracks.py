from app.database import SessionLocal
from app.repositories.track_repository import TrackRepository
from app.schemas.track import TrackCreate


def test_empty_catalog(client):
    response = client.get("/api/v1/tracks")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "page": 1, "page_size": 50}


def test_catalog_list_pagination_and_search(client, tmp_path):
    audio = tmp_path / "rock.mp3"
    audio.write_bytes(b"audio")
    with SessionLocal() as db:
        repo = TrackRepository(db)
        repo.create(
            TrackCreate(
                title="First Rock Song",
                artist="Example Artist",
                album="Demo Album",
                genre="Rock",
                file_path=str(audio),
                file_size=audio.stat().st_size,
            )
        )
        repo.create(
            TrackCreate(
                title="Second Jazz Song",
                artist="Other Artist",
                album="Other Album",
                genre="Jazz",
                file_path=str(audio),
                file_size=audio.stat().st_size,
            )
        )

    response = client.get("/api/v1/tracks?page=1&page_size=1")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 1
    assert len(body["items"]) == 1

    search = client.get("/api/v1/tracks?q=rock")
    search_body = search.json()

    assert search.status_code == 200
    assert search_body["total"] == 1
    assert search_body["items"][0]["title"] == "First Rock Song"


def test_track_detail_not_found(client):
    response = client.get("/api/v1/tracks/9999")

    assert response.status_code == 404
