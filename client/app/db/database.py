import os
import sqlite3
from pathlib import Path


def app_data_dir() -> Path:
    base = Path(os.environ.get("EUREKA_DATA_DIR", Path.home() / ".local" / "share" / "eureka-music"))
    (base / "tracks").mkdir(parents=True, exist_ok=True)
    (base / "logs").mkdir(parents=True, exist_ok=True)
    return base


def database_path() -> Path:
    return app_data_dir() / "library.db"


def get_connection(path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or database_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> None:
    owns_connection = conn is None
    connection = conn or get_connection()
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS local_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_track_id INTEGER UNIQUE,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,
                genre TEXT,
                file_path TEXT NOT NULL,
                duration_ms INTEGER,
                downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY (playlist_id, track_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (track_id) REFERENCES local_tracks(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_playlist_position
            ON playlist_tracks(playlist_id, position);
            """
        )
        connection.commit()
    finally:
        if owns_connection:
            connection.close()
