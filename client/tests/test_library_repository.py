from app.db.database import get_connection, init_db
from app.db.repositories import LibraryRepository


def test_insert_and_query_local_track(conn, tmp_path):
    repo = LibraryRepository(conn)
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")

    track = repo.upsert_local_track(
        server_track_id=10,
        title="Local Song",
        artist="Artist",
        album="Album",
        genre="Rock",
        file_path=str(audio),
    )

    assert track.id is not None
    assert repo.get(track.id).title == "Local Song"
    assert repo.get_by_server_id(10).artist == "Artist"


def test_duplicate_server_id_updates_existing_track(conn, tmp_path):
    repo = LibraryRepository(conn)
    first = tmp_path / "first.mp3"
    second = tmp_path / "second.mp3"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    original = repo.upsert_local_track(
        server_track_id=5,
        title="Old",
        artist=None,
        album=None,
        genre=None,
        file_path=str(first),
    )
    updated = repo.upsert_local_track(
        server_track_id=5,
        title="New",
        artist="Artist",
        album=None,
        genre=None,
        file_path=str(second),
    )

    assert updated.id == original.id
    assert repo.get_by_server_id(5).title == "New"
    assert len(repo.list_tracks()) == 1


def test_library_persists_after_reopen(tmp_path):
    db_path = tmp_path / "library.db"
    conn = get_connection(db_path)
    init_db(conn)
    repo = LibraryRepository(conn)
    repo.upsert_local_track(
        server_track_id=1,
        title="Persistent",
        artist=None,
        album=None,
        genre=None,
        file_path=str(tmp_path / "p.mp3"),
    )
    conn.close()

    reopened = get_connection(db_path)
    try:
        assert LibraryRepository(reopened).get_by_server_id(1).title == "Persistent"
    finally:
        reopened.close()
