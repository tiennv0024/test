# Eureka Music Design

## 1. Problem Statement

Build a local music application for Ubuntu with a FastAPI server, PostgreSQL catalog, PySide2 desktop client, local playback, playlists, upload/download, persistence, and responsive UI behavior.

## 2. Requirements

The system supports FMA Small ingestion, paginated catalog browsing, search, track download, upload, local library browsing, playback controls, playlist ordering, shuffle, loop, and crash-resistant persistence.

## 3. Assumptions

- Ubuntu 22.04 and Python 3.10 are the target runtime.
- FMA Small is extracted locally and is not committed.
- Audio binaries belong on disk. Databases store metadata and references only.
- Authentication is out of scope for the assignment.

## 4. System Architecture

The desktop client communicates with the server over REST. The server stores catalog metadata in PostgreSQL and stores audio under a mounted filesystem path. The client stores downloaded metadata and playlists in SQLite and downloaded audio under the user data directory.

## 5. Server Architecture

Server code follows:

```text
API router -> service -> repository -> SQLAlchemy -> PostgreSQL
```

The API layer validates HTTP inputs and status codes. The service layer owns upload/download rules and safe file operations. The repository layer owns queries.

## 6. Client Architecture

Client code follows:

```text
UI -> services/workers -> repositories/API client/playback -> SQLite/HTTP/QMediaPlayer
```

Network and file operations run in `QThread` workers so the Qt event loop stays responsive.

## 7. Database Design

PostgreSQL has a `tracks` table for server catalog metadata. SQLite has `local_tracks`, `playlists`, and `playlist_tracks` for local library and playlist state.

## 8. REST API Design

- `GET /health`
- `GET /api/v1/tracks`
- `GET /api/v1/tracks/{track_id}`
- `GET /api/v1/tracks/{track_id}/download`
- `POST /api/v1/tracks`

List endpoints are paginated with `page` and `page_size` to avoid transferring the whole FMA catalog.

## 9. Qt Threading Model

Catalog loading, downloads, and uploads are implemented with worker objects moved to `QThread`. Workers emit success/failure signals, and UI widgets update only from the main thread.

## 10. Playback Architecture

`PlaybackService` wraps `QMediaPlayer`. The bottom `PlayerWidget` controls play/pause, stop, and seek. `PlaybackQueue` contains pure queue logic for next, previous, shuffle, and loop behavior.

## 11. Persistence Strategy

PostgreSQL persists server metadata. SQLite commits after each local mutation, including playlist changes and downloaded-track registration. File writes use temporary files followed by atomic rename.

## 12. Error Handling

Recoverable server errors return predictable HTTP status codes. Client workers surface failures via signals and message boxes instead of crashing the app.

## 13. Reliability

The design does not rely on shutdown hooks. Completed writes are registered after files are present. Incomplete `.part` files are not inserted into SQLite.

## 14. Performance

The client uses `QTableView`/`QAbstractTableModel`, not per-row widgets. Startup reads lightweight SQLite metadata and avoids scanning all audio files.

## 15. Memory Management

Audio files are streamed or passed to Qt by path. The app avoids caching binary audio in memory. Worker threads are removed when finished.

## 16. Security Considerations

Uploads validate extensions, generate internal filenames, avoid trusting original paths, write to temp files first, and clean temporary files on failure.

## 17. Trade-offs

REST was chosen because the required operations are request/response based. Filesystem audio storage keeps PostgreSQL small. SQLite provides zero-admin local persistence. Qt model/view keeps large tables efficient.

## 18. AI Usage

AI assistance was used to decompose requirements, draft architecture, generate implementation scaffolding, and produce tests/documentation. The implementation remains reviewable and explainable by the author.
