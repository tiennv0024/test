from app.db.repositories import LibraryRepository, PlaylistRepository
from app.services.playlist_service import PlaylistService


def _track(repo: LibraryRepository, title: str):
    return repo.upsert_local_track(
        server_track_id=None,
        title=title,
        artist=None,
        album=None,
        genre=None,
        file_path=f"/tmp/{title}.mp3",
    )


def test_playlist_create_add_remove_reorder_persists(conn):
    library = LibraryRepository(conn)
    service = PlaylistService(PlaylistRepository(conn))
    first = _track(library, "First")
    second = _track(library, "Second")
    third = _track(library, "Third")

    playlist = service.create("Demo")
    service.add_track(playlist.id, first.id)
    service.add_track(playlist.id, second.id)
    service.add_track(playlist.id, third.id)
    service.reorder(playlist.id, [third.id, first.id, second.id])

    assert [track.title for track in service.tracks(playlist.id)] == ["Third", "First", "Second"]

    service.remove_track(playlist.id, first.id)

    assert [track.title for track in service.tracks(playlist.id)] == ["Third", "Second"]


def test_playlist_name_required(conn):
    service = PlaylistService(PlaylistRepository(conn))

    try:
        service.create("   ")
    except ValueError as exc:
        assert "required" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
