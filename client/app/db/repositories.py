import sqlite3
from pathlib import Path

from app.models.track import Playlist, Track


class LibraryRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_local_track(
        self,
        *,
        server_track_id: int | None,
        title: str,
        artist: str | None,
        album: str | None,
        genre: str | None,
        file_path: str,
        duration_ms: int | None = None,
    ) -> Track:
        if server_track_id is not None:
            existing = self.conn.execute(
                "SELECT id FROM local_tracks WHERE server_track_id = ?",
                (server_track_id,),
            ).fetchone()
            if existing:
                self.conn.execute(
                    """
                    UPDATE local_tracks
                    SET title = ?, artist = ?, album = ?, genre = ?, file_path = ?, duration_ms = ?
                    WHERE server_track_id = ?
                    """,
                    (title, artist, album, genre, file_path, duration_ms, server_track_id),
                )
                self.conn.commit()
                return self.get(existing["id"])  # type: ignore[return-value]

        cursor = self.conn.execute(
            """
            INSERT INTO local_tracks
                (server_track_id, title, artist, album, genre, file_path, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (server_track_id, title, artist, album, genre, file_path, duration_ms),
        )
        self.conn.commit()
        return self.get(int(cursor.lastrowid))  # type: ignore[return-value]

    def list_tracks(self) -> list[Track]:
        rows = self.conn.execute("SELECT * FROM local_tracks ORDER BY title COLLATE NOCASE").fetchall()
        return [self._row_to_track(row) for row in rows]

    def get(self, track_id: int) -> Track | None:
        row = self.conn.execute("SELECT * FROM local_tracks WHERE id = ?", (track_id,)).fetchone()
        return self._row_to_track(row) if row else None

    def get_by_server_id(self, server_track_id: int) -> Track | None:
        row = self.conn.execute(
            "SELECT * FROM local_tracks WHERE server_track_id = ?",
            (server_track_id,),
        ).fetchone()
        return self._row_to_track(row) if row else None

    @staticmethod
    def _row_to_track(row: sqlite3.Row) -> Track:
        return Track(
            id=row["id"],
            server_track_id=row["server_track_id"],
            title=row["title"],
            artist=row["artist"],
            album=row["album"],
            genre=row["genre"],
            file_path=row["file_path"],
            duration_ms=row["duration_ms"],
        )


class PlaylistRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_playlist(self, name: str) -> Playlist:
        cursor = self.conn.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        self.conn.commit()
        return Playlist(id=int(cursor.lastrowid), name=name)

    def list_playlists(self) -> list[Playlist]:
        rows = self.conn.execute("SELECT id, name FROM playlists ORDER BY created_at, id").fetchall()
        return [Playlist(id=row["id"], name=row["name"]) for row in rows]

    def add_track(self, playlist_id: int, track_id: int) -> None:
        next_position = self._next_position(playlist_id)
        self.conn.execute(
            """
            INSERT OR REPLACE INTO playlist_tracks (playlist_id, track_id, position)
            VALUES (?, ?, ?)
            """,
            (playlist_id, track_id, next_position),
        )
        self.conn.commit()

    def remove_track(self, playlist_id: int, track_id: int) -> None:
        self.conn.execute(
            "DELETE FROM playlist_tracks WHERE playlist_id = ? AND track_id = ?",
            (playlist_id, track_id),
        )
        self._rewrite_positions(playlist_id)
        self.conn.commit()

    def reorder(self, playlist_id: int, track_ids: list[int]) -> None:
        with self.conn:
            for position, track_id in enumerate(track_ids):
                self.conn.execute(
                    """
                    UPDATE playlist_tracks
                    SET position = ?
                    WHERE playlist_id = ? AND track_id = ?
                    """,
                    (position, playlist_id, track_id),
                )

    def playlist_tracks(self, playlist_id: int) -> list[Track]:
        rows = self.conn.execute(
            """
            SELECT lt.*
            FROM playlist_tracks pt
            JOIN local_tracks lt ON lt.id = pt.track_id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
            """,
            (playlist_id,),
        ).fetchall()
        return [LibraryRepository._row_to_track(row) for row in rows]

    def _next_position(self, playlist_id: int) -> int:
        value = self.conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 AS next_position FROM playlist_tracks WHERE playlist_id = ?",
            (playlist_id,),
        ).fetchone()
        return int(value["next_position"])

    def _rewrite_positions(self, playlist_id: int) -> None:
        rows = self.conn.execute(
            "SELECT track_id FROM playlist_tracks WHERE playlist_id = ? ORDER BY position",
            (playlist_id,),
        ).fetchall()
        for position, row in enumerate(rows):
            self.conn.execute(
                "UPDATE playlist_tracks SET position = ? WHERE playlist_id = ? AND track_id = ?",
                (position, playlist_id, row["track_id"]),
            )


def remove_file_if_unreferenced(path: str) -> None:
    candidate = Path(path)
    if candidate.exists() and candidate.is_file():
        candidate.unlink()
