# CODEX_IMPLEMENTATION.md

# Eureka Music App System — Codex Implementation Specification

## 1. Objective

Build a complete music application system for Ubuntu within the assignment scope.

The solution MUST include:

1. A backend server.
2. A desktop client.
3. FMA Small dataset support.
4. Local playback.
5. Playlist management.
6. Upload/download between client and server.
7. Persistence after hard kill / reboot.
8. Stable memory usage.
9. Responsive UI with no blocking operations.
10. Documentation and software diagrams.

The final solution is expected to run on Ubuntu 20.04, 22.04, or 24.04.

Recommended development target:

- Ubuntu 22.04
- Python 3.10

---

# 2. Mandatory Assignment Requirements

## 2.1 Server

The backend MUST:

- Use FastAPI.
- Use PostgreSQL.
- Store the song catalog.
- Store references to audio files.
- Allow the client to:
  - list tracks;
  - search tracks;
  - download tracks;
  - upload tracks.
- Run as a Docker image.
- Be runnable using Docker Compose.
- Be the source of truth for the server music catalog.
- NOT depend on Spotify, YouTube, or third-party music services.

Recommended API style:

- REST over HTTP.

Reason:

- All mandatory operations are request/response oriented.
- No mandatory real-time server push requirement exists.
- REST is simple to test, document, and explain.

---

## 2.2 Desktop Client

The client MUST:

- Be written in Python 3 and/or C++.
- Use `PySide2==5.15.x` for UI.
- Run from a Python virtual environment.
- Browse tracks available on the server.
- Search the server catalog.
- Download songs.
- Browse locally downloaded songs.
- Play downloaded songs locally.
- Support:
  - play;
  - stop;
  - pause/continue;
  - seek/jump to a specific position.
- Create playlists.
- Support playlist:
  - manual ordering;
  - shuffle;
  - loop playback.
- Upload local audio files to the server.

SQLite SHOULD be used for client-side local persistence.

---

# 3. Non-Functional Requirements

These are first-class requirements and MUST NOT be treated as optional.

## 3.1 UI Responsiveness

The desktop application MUST never freeze or hang during:

- API requests;
- searching;
- downloading;
- uploading;
- local file operations;
- database access;
- metadata parsing.

Long-running or blocking operations MUST NOT run on the Qt main/UI thread.

Use:

- `QThread`;
- worker objects;
- Qt signals/slots.

---

## 3.2 Startup Performance

The client MUST start in under 10 seconds on a typical laptop, including when handling a few thousand tracks.

Target engineering goal:

- Prefer startup under 2–3 seconds on the full FMA Small dataset.

DO NOT:

- create thousands of QWidget instances at startup;
- scan and parse every MP3 file at startup;
- load audio binaries into memory.

Use:

- SQLite metadata;
- `QTableView`;
- `QAbstractTableModel`;
- pagination or lazy loading.

---

## 3.3 Persistence

Data MUST survive:

- normal application close;
- reboot;
- `SIGKILL`;
- forced termination.

Important:

Do NOT rely on application shutdown handlers to save important state.

Persist state immediately after mutation.

Examples:

- playlist creation;
- playlist deletion;
- playlist ordering;
- downloaded track registration;
- local library changes.

---

## 3.4 Memory Stability

Memory usage MUST remain reasonably stable during:

- browsing;
- searching;
- downloading;
- uploading;
- repeated playback;
- playlist operations.

Avoid:

- keeping full audio files in RAM;
- leaking QThreads;
- accumulating signal connections;
- recreating large view hierarchies unnecessarily;
- holding old network responses;
- unbounded image/audio caches.

---

# 4. Dataset Requirements

Use the FMA Small dataset.

Expected dataset:

- approximately 8,000 tracks;
- 30-second audio clips;
- 8 balanced genres.

Metadata comes from `fma_metadata`, especially `tracks.csv`.

The project MUST provide seed scripts for BOTH:

- server;
- client.

Each seed command MUST accept the path to the extracted FMA folder.

Examples:

```bash
python seed.py /path/to/fma
```

During development, support:

```bash
python seed.py /path/to/fma --limit 100
```

Final testing MUST be performed on the full dataset.

DO NOT commit the dataset into Git.

---

# 5. Recommended Technology Stack

## Server

- Python 3.10
- FastAPI
- Uvicorn
- PostgreSQL 16
- SQLAlchemy
- Alembic
- psycopg2-binary
- Pydantic Settings
- python-multipart
- Mutagen
- pytest
- httpx

## Client

- Python 3.10
- PySide2 5.15.2.1
- requests
- sqlite3
- QtMultimedia
- Mutagen
- pytest

## Engineering

- Ruff
- type hints
- logging
- Git
- Docker
- Docker Compose

---

# 6. Repository Structure

Create the repository with this structure:

```text
eureka-music/
├── README.md
├── DESIGN.md
├── AGENTS.md
├── SKILLS.md
├── .gitignore
├── docker-compose.yml
│
├── docs/
│   └── diagrams/
│       ├── context.puml
│       ├── container.puml
│       ├── server-components.puml
│       ├── client-components.puml
│       ├── erd.puml
│       ├── sequence-download.puml
│       ├── sequence-upload.puml
│       └── sequence-playback.puml
│
├── server/
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── seed.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── tracks.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── track.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── track.py
│   │   │
│   │   ├── repositories/
│   │   │   └── track_repository.py
│   │   │
│   │   └── services/
│   │       └── track_service.py
│   │
│   ├── storage/
│   │   └── tracks/
│   │
│   └── tests/
│       ├── test_health.py
│       ├── test_tracks.py
│       ├── test_download.py
│       └── test_upload.py
│
└── client/
    ├── README.md
    ├── requirements.txt
    ├── seed.py
    │
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   │
    │   ├── ui/
    │   │   ├── main_window.py
    │   │   ├── catalog_page.py
    │   │   ├── library_page.py
    │   │   ├── playlist_page.py
    │   │   ├── upload_page.py
    │   │   └── player_widget.py
    │   │
    │   ├── api/
    │   │   └── api_client.py
    │   │
    │   ├── db/
    │   │   ├── database.py
    │   │   └── repositories.py
    │   │
    │   ├── models/
    │   │   └── track.py
    │   │
    │   ├── services/
    │   │   ├── library_service.py
    │   │   ├── playlist_service.py
    │   │   └── playback_service.py
    │   │
    │   └── workers/
    │       ├── catalog_worker.py
    │       ├── download_worker.py
    │       └── upload_worker.py
    │
    ├── storage/
    │   └── tracks/
    │
    └── tests/
        ├── test_library_repository.py
        ├── test_playlist_service.py
        └── test_playback_queue.py
```

---

# 7. Git Rules

Maintain real commit history.

DO NOT squash everything into one final commit.

Use meaningful commits such as:

```text
chore: initialize repository
feat(server): initialize FastAPI service
feat(server): add PostgreSQL persistence
feat(server): implement FMA seed command
feat(server): add catalog search and pagination
feat(server): implement track download
feat(server): implement track upload
feat(client): initialize PySide2 application
feat(client): add local SQLite library
feat(client): implement async catalog loading
feat(client): implement track download
feat(client): implement local playback
feat(client): add playlist persistence
feat(client): implement shuffle and loop
feat(client): implement upload workflow
test: add server API tests
perf: optimize track table rendering
docs: add architecture documentation
```

---

# 8. Server Implementation

## 8.1 Requirements File

Create:

`server/requirements.txt`

Recommended dependencies:

```text
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
pydantic-settings
python-multipart
alembic
mutagen
pytest
httpx
```

---

## 8.2 PostgreSQL / Docker Compose

Create root `docker-compose.yml`.

Requirements:

- PostgreSQL container.
- FastAPI container.
- persistent PostgreSQL volume.
- audio storage volume/bind mount.
- PostgreSQL healthcheck.
- FastAPI waits for PostgreSQL health.

Recommended configuration:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: eureka_music
      POSTGRES_USER: eureka
      POSTGRES_PASSWORD: eureka
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U eureka -d eureka_music"]
      interval: 5s
      timeout: 5s
      retries: 10

  server:
    build:
      context: ./server
    environment:
      DATABASE_URL: postgresql://eureka:eureka@postgres:5432/eureka_music
      AUDIO_STORAGE_PATH: /app/storage/tracks
    volumes:
      - ./server/storage:/app/storage
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

---

# 9. Server Database Model

Create a `tracks` table.

Minimum fields:

```text
id              BIGINT PRIMARY KEY
fma_id          INTEGER UNIQUE NULLABLE
title           VARCHAR(255) NOT NULL
artist          VARCHAR(255)
album           VARCHAR(255)
genre           VARCHAR(255)
tags            TEXT or JSONB
file_path       TEXT NOT NULL
duration_ms     INTEGER
file_size       BIGINT
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

Indexes SHOULD exist for:

- title;
- artist;
- genre;
- fma_id.

The database stores metadata only.

DO NOT store MP3 binary data in PostgreSQL.

Audio files belong in filesystem storage.

---

# 10. Server Layering

Use this dependency direction:

```text
API Router
    ↓
Service
    ↓
Repository
    ↓
SQLAlchemy
    ↓
PostgreSQL
```

Rules:

- API routes MUST NOT contain large business logic.
- Repository handles database queries.
- Service handles application/business rules.
- Pydantic models define API contracts.
- DB models MUST NOT be blindly exposed as public API schemas.

---

# 11. Server API Contract

Implement at minimum:

## Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Track List

```http
GET /api/v1/tracks
```

Query parameters:

```text
page
page_size
q
```

Example:

```http
GET /api/v1/tracks?page=1&page_size=50&q=rock
```

Response:

```json
{
  "items": [],
  "total": 8000,
  "page": 1,
  "page_size": 50
}
```

Rules:

- `page >= 1`.
- `1 <= page_size <= 100`.
- Search title, artist, album, genre.
- Use server-side pagination.
- Do not return 8,000 items in one request.

---

## Track Detail

Recommended:

```http
GET /api/v1/tracks/{track_id}
```

---

## Download

```http
GET /api/v1/tracks/{track_id}/download
```

Requirements:

- Return file using streaming/FileResponse.
- Return 404 if track does not exist.
- Return 404 if DB record exists but audio file is missing.

---

## Upload

```http
POST /api/v1/tracks
Content-Type: multipart/form-data
```

Fields:

```text
file
title
artist
album
genre
```

Requirements:

- validate file type;
- generate an internal storage filename;
- DO NOT trust the original filename as filesystem path;
- write to a temporary file first;
- finalize using atomic rename;
- only insert the DB record after the file is safely persisted;
- clean temporary files on failure.

---

# 12. FMA Server Seed Script

Implement:

```bash
python server/seed.py /path/to/fma
```

Support:

```bash
python server/seed.py /path/to/fma --limit 100
```

Expected input structure resembles:

```text
fma/
├── fma_small/
│   ├── 000/
│   │   ├── 000002.mp3
│   │   └── ...
│   └── ...
│
└── fma_metadata/
    └── tracks.csv
```

Implement an FMA track path helper.

For track ID `2`:

```text
000002.mp3
```

Directory:

```text
000
```

Example concept:

```python
def get_audio_path(root, track_id):
    value = f"{track_id:06d}"
    folder = value[:3]
    return root / "fma_small" / folder / f"{value}.mp3"
```

Important:

`tracks.csv` uses complex/multi-level headers.

The parser MUST be validated against the real dataset.

Development sequence:

1. seed 10 tracks;
2. validate metadata;
3. seed 100 tracks;
4. validate APIs;
5. seed all tracks.

The full seed should create approximately 8,000 server records.

Seed MUST be idempotent or safely handle duplicates.

---

# 13. Client Requirements

Create:

`client/requirements.txt`

Minimum:

```text
PySide2==5.15.2.1
requests
mutagen
pytest
```

Client MUST run from a virtual environment.

Example:

```bash
cd client
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

---

# 14. Client UI Structure

Recommended primary layout:

```text
┌─────────────────────────────────────────────────────────┐
│ Eureka Music                                            │
├───────────────┬─────────────────────────────────────────┤
│ Navigation    │ Main Content                            │
│               │                                         │
│ Catalog       │                                         │
│ Library       │                                         │
│ Playlists     │                                         │
│ Upload        │                                         │
│               │                                         │
├───────────────┴─────────────────────────────────────────┤
│ Now Playing / Seek / Playback Controls                  │
└─────────────────────────────────────────────────────────┘
```

Use a shared bottom player widget.

Primary pages:

- Catalog.
- Library.
- Playlists.
- Upload.

Do NOT spend excessive time on visual polish before functionality is complete.

---

# 15. Client Local Storage

Recommended application data directory:

```text
~/.local/share/eureka-music/
├── library.db
├── tracks/
└── logs/
```

Use a platform-appropriate Qt data location if convenient.

---

# 16. SQLite Schema

## local_tracks

```sql
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
```

Important:

Use a separate client local ID.

Do NOT assume:

```text
client local ID == server ID
```

`server_track_id` may be nullable for tracks seeded directly into the local client.

---

## playlists

```sql
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## playlist_tracks

```sql
CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, track_id)
);
```

Index:

```sql
CREATE INDEX IF NOT EXISTS idx_playlist_position
ON playlist_tracks(playlist_id, position);
```

---

# 17. Client Architecture

Use this general separation:

```text
UI
 ↓
Services / Controllers
 ↓
Repositories / API Client / Workers
 ↓
SQLite / HTTP / QMediaPlayer
```

Recommended services:

```text
ApiClient
LibraryService
PlaylistService
PlaybackService
```

Recommended workers:

```text
CatalogWorker
DownloadWorker
UploadWorker
```

---

# 18. Qt Threading Rules

THIS SECTION IS CRITICAL.

The Qt main thread MUST NOT execute blocking:

- `requests.get`;
- `requests.post`;
- large file reads/writes;
- dataset parsing;
- slow SQLite operations;
- network downloads;
- network uploads.

Use worker objects + QThread.

Pattern:

```text
Main UI
   │
   │ user action
   ▼
Worker object
   │
   │ moveToThread()
   ▼
QThread
   │
   │ blocking operation
   ▼
Signal result
   │
   ▼
Main UI update
```

Worker MUST communicate using Qt signals.

NEVER modify Qt widgets from a worker thread.

Clean threads properly:

```python
worker.finished.connect(thread.quit)
worker.finished.connect(worker.deleteLater)
thread.finished.connect(thread.deleteLater)
```

Also clean up on failure.

---

# 19. Server Catalog Page

Use:

```text
QTableView
+
QAbstractTableModel
```

DO NOT create one custom QWidget row for each track.

Recommended columns:

```text
Title
Artist
Album
Genre
```

Actions can be exposed with:

- selection + Download button;
- double click;
- context menu.

Avoid embedding 8,000 QPushButtons in the table.

---

# 20. Pagination

Server and UI MUST use pagination.

Recommended page size:

```text
50
```

At 8,000 tracks:

```text
~160 pages
```

Provide:

```text
Previous
Next
Current Page
Total Results
```

Optional:

- page number input.

---

# 21. Search

Implement search against server catalog.

Use search debounce.

Recommended:

```text
300 ms
```

Flow:

```text
textChanged
    ↓
restart QTimer
    ↓
300ms timeout
    ↓
start CatalogWorker
    ↓
GET /tracks?q=...
    ↓
update table model
```

Do NOT call the API for every keystroke immediately.

---

# 22. Download Flow

Required sequence:

```text
User selects track
    ↓
Download button
    ↓
DownloadWorker
    ↓
GET /api/v1/tracks/{id}/download
    ↓
write <file>.part using chunks
    ↓
download complete
    ↓
atomic rename to final filename
    ↓
SQLite INSERT
    ↓
emit finished
    ↓
refresh Library
```

Use streaming HTTP.

Example concept:

```python
response = session.get(url, stream=True, timeout=30)
response.raise_for_status()

with open(temp_path, "wb") as handle:
    for chunk in response.iter_content(chunk_size=64 * 1024):
        if chunk:
            handle.write(chunk)
```

DO NOT:

```python
audio_bytes = response.content
```

for large downloads.

---

# 23. Download Progress

Use `Content-Length` if available.

Worker signal:

```python
progress_changed = Signal(int)
```

UI should show:

```text
Downloading...
73%
```

The UI MUST remain responsive while downloading.

---

# 24. Download Failure Safety

Use:

```text
track.mp3.part
```

during download.

Only after successful completion:

```text
atomic rename
track.mp3
```

Only after successful rename:

```text
INSERT local_tracks
COMMIT
```

If application is killed mid-download:

- `.part` may remain;
- it MUST NOT appear as a valid downloaded track.

At startup, optional cleanup may remove old `.part` files.

---

# 25. Local Library

Library page MUST read metadata from SQLite.

DO NOT scan and parse all local MP3 files at startup.

Flow:

```text
SQLite
 ↓
QAbstractTableModel
 ↓
QTableView
```

Double-clicking a track SHOULD play it.

---

# 26. Playback Service

Use `QMediaPlayer`.

Minimum operations:

```text
load
play
pause
continue
stop
seek
```

Track loading concept:

```python
url = QUrl.fromLocalFile(file_path)
content = QMediaContent(url)
player.setMedia(content)
```

Listen to:

```text
positionChanged
durationChanged
stateChanged
mediaStatusChanged
```

---

# 27. Player Widget

Minimum UI:

```text
Track Title — Artist

00:08  ━━━━━━━━━━━━━━━━━━━━━━━━━━━  00:30

Previous    Play/Pause    Stop    Next
```

Seek behavior:

```text
slider movement
   ↓
player.setPosition(milliseconds)
```

The UI MUST reflect current position.

---

# 28. Playlist Persistence

Support:

- create playlist;
- delete playlist;
- add track;
- remove track;
- reorder manually;
- shuffle playback;
- loop playback.

Persist every structural change immediately.

Example:

```text
User reorders track
   ↓
BEGIN TRANSACTION
   ↓
UPDATE positions
   ↓
COMMIT
   ↓
UI state accepted
```

Do NOT wait until app shutdown.

---

# 29. Manual Reorder

Use Qt drag/drop if practical:

```text
QListView or QTableView
```

with internal move.

After reorder, rewrite:

```text
playlist_tracks.position
```

Example:

Before:

```text
A 1
B 2
C 3
```

After moving C to top:

```text
C 1
A 2
B 3
```

Persistence MUST survive SIGKILL.

---

# 30. Playback Queue

Do NOT directly mutate persistent playlist order when shuffle is enabled.

Create a runtime queue:

```text
Persistent Playlist
       ↓
PlaybackQueue
       ↓
QMediaPlayer
```

Example persistent order:

```text
A B C D
```

Shuffle queue:

```text
C A D B
```

Persistent DB stays:

```text
A B C D
```

Suggested class:

```python
class PlaybackQueue:
    track_ids: list[int]
    current_index: int
    shuffle_enabled: bool
    loop_mode: str
```

---

# 31. Loop

Minimum loop modes:

```text
OFF
ALL
```

Optional:

```text
ONE
```

Behavior when current track finishes:

```text
if another queue item exists:
    play next
elif loop == ALL:
    restart queue
elif loop == ONE:
    replay current
else:
    stop
```

---

# 32. Upload Page

Minimum fields:

```text
File
Title
Artist
Album
Genre
```

Use an UploadWorker.

Flow:

```text
Choose local file
    ↓
validate
    ↓
UploadWorker
    ↓
POST multipart/form-data
    ↓
server stores file
    ↓
server inserts DB
    ↓
worker emits success
    ↓
refresh catalog
```

Upload MUST NOT block the UI.

Provide:

- progress if practical;
- clear success indication;
- clear failure message.

---

# 33. Client Seed Script

Implement:

```bash
python client/seed.py /path/to/fma
```

Support:

```bash
python client/seed.py /path/to/fma --limit 100
```

The client seed should:

1. parse FMA metadata;
2. copy/link local audio into client local storage;
3. insert corresponding SQLite metadata.

This allows full local playback testing without manually downloading thousands of files.

---

# 34. Error Handling

Define predictable error paths.

Possible groups:

```text
ApiError
NetworkError
DownloadError
UploadError
PlaybackError
DatabaseError
```

Expected UX:

Server unavailable:

```text
Unable to connect to music server.
[Retry]
```

Track missing:

```text
Audio file is unavailable.
```

Invalid upload:

```text
Selected file is not a supported audio file.
```

DO NOT crash the whole application for recoverable user/network errors.

---

# 35. Logging

Use Python `logging`.

Server SHOULD log:

- startup;
- request failures;
- uploads;
- missing files;
- database errors.

Client SHOULD log:

- startup duration;
- worker failures;
- downloads;
- uploads;
- playback errors;
- database failures.

DO NOT use uncontrolled `print()` debugging in final code.

---

# 36. Server Tests

At minimum implement:

```text
test_health.py
test_tracks.py
test_download.py
test_upload.py
```

Test:

- `/health`;
- empty catalog;
- catalog list;
- pagination;
- search;
- not-found track;
- valid download;
- missing audio file;
- valid upload;
- invalid upload.

---

# 37. Client Tests

Focus on logic rather than pixel-level UI tests.

At minimum:

## Library Repository

Test:

- insert local track;
- query;
- duplicate server ID handling;
- persistence after DB reopen.

## Playlist Service

Test:

- create;
- add;
- remove;
- reorder;
- persisted ordering.

## Playback Queue

Test:

- next;
- previous;
- shuffle retains same set;
- loop behavior.

---

# 38. Hard-Kill Reliability Test

Manual acceptance test:

1. Start client.
2. Create a playlist.
3. Add several tracks.
4. Reorder tracks.
5. Download a track.
6. Find process ID.
7. Execute:

```bash
kill -9 <PID>
```

8. Restart client.

Expected:

- playlist exists;
- order is preserved;
- completed downloads exist;
- incomplete downloads are not registered as completed tracks;
- SQLite is readable;
- app starts normally.

---

# 39. Full Dataset Performance Test

Seed all FMA Small tracks.

Verify:

```sql
SELECT COUNT(*) FROM tracks;
```

Expected:

```text
approximately 8000
```

Then test:

- startup;
- browse first page;
- next/previous pages;
- search repeatedly;
- download;
- playback;
- playlist operations;
- upload.

---

# 40. Startup Benchmark

Measure client startup using `time.perf_counter()`.

Measure from application start until:

- main window is displayed;
- initial local metadata is usable.

Log:

```text
Startup completed in X.XXX seconds
```

Mandatory:

```text
< 10 seconds
```

Preferred:

```text
< 2–3 seconds
```

---

# 41. Memory Test

On Linux use:

```bash
ps -o pid,rss,cmd -p <PID>
```

or:

```bash
htop
```

Test workflow:

1. start application;
2. browse catalog;
3. run many searches;
4. download tracks;
5. play many tracks;
6. create/reorder playlists;
7. upload tracks.

Memory SHOULD stabilize.

Investigate if RSS grows continuously.

Likely causes:

- leaked threads;
- leaked QObject references;
- repeated signal connections;
- unreleased workers;
- cached binary data;
- unnecessary widgets.

---

# 42. UI Performance Rules

DO:

- use model/view;
- update only necessary data;
- paginate server data;
- use background workers;
- cache lightweight metadata appropriately.

DO NOT:

- build thousands of row widgets;
- scan all MP3 files on startup;
- block Qt event loop;
- decode/load every audio file in advance.

---

# 43. API Documentation

FastAPI provides:

```text
/docs
/redoc
```

Ensure:

- request/response schemas are defined;
- endpoint names are clear;
- status codes are correct;
- descriptions are useful.

---

# 44. DESIGN.md

Create `DESIGN.md` with at least:

```text
1. Problem Statement
2. Requirements
3. Assumptions
4. System Architecture
5. Server Architecture
6. Client Architecture
7. Database Design
8. REST API Design
9. Qt Threading Model
10. Playback Architecture
11. Persistence Strategy
12. Error Handling
13. Reliability
14. Performance
15. Memory Management
16. Security Considerations
17. Trade-offs
18. AI Usage
```

---

# 45. Required Diagrams

Create source-controlled diagrams.

PlantUML is recommended.

At minimum:

## Context Diagram

Actors:

```text
User
Desktop Client
Eureka Music Server
```

---

## Container Diagram

Include:

```text
PySide2 Client
SQLite
FastAPI
PostgreSQL
Audio Filesystem
```

---

## Server Component Diagram

```text
Router
Service
Repository
SQLAlchemy
PostgreSQL
Filesystem
```

---

## Client Component Diagram

```text
Views
Services
Workers
ApiClient
Repositories
SQLite
PlaybackService
QMediaPlayer
```

---

## ERD

Include both:

- PostgreSQL server schema;
- SQLite client schema.

---

## Download Sequence

```text
User
UI
DownloadWorker
FastAPI
Filesystem
SQLite
```

---

## Upload Sequence

```text
User
UI
UploadWorker
FastAPI
Filesystem
PostgreSQL
```

---

## Playback Sequence

```text
User
UI
PlaybackService
QMediaPlayer
UI signals
```

---

# 46. AGENTS.md

Document how AI was used.

Suggested content:

```text
AI was used for:

- requirement decomposition;
- architecture brainstorming;
- diagram drafting;
- implementation suggestions;
- code review;
- test-case generation;
- documentation review.

All generated code and recommendations were reviewed,
tested, and adapted by the author.

The author remains responsible for architecture,
implementation, debugging, and final engineering decisions.
```

Do NOT imply that AI blindly generated the entire project.

---

# 47. SKILLS.md

Document demonstrated skills.

Suggested sections:

```text
Backend
- FastAPI
- REST
- PostgreSQL
- SQLAlchemy
- Docker

Desktop
- Python
- PySide2
- Qt Model/View
- QThread
- Qt Multimedia

Data
- SQLite
- FMA ingestion

Engineering
- testing
- type hints
- logging
- error handling
- performance optimization
- persistence
- memory management

Architecture
- C4
- ERD
- sequence diagrams
```

---

# 48. README Requirements

The root README MUST make the project easy to run.

Include:

```text
Project Overview
Architecture
Prerequisites
Quick Start
Start Server
Seed Server
Start Client
Seed Client
Run Tests
Performance Notes
Known Limitations
Demo Flow
```

Server startup SHOULD be as close as possible to:

```bash
docker compose up --build
```

Client startup:

```bash
cd client
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

---

# 49. Priority Levels

## P0 — Mandatory

Implement first:

```text
Docker Compose
FastAPI
PostgreSQL
FMA server seed
catalog list
search
pagination
download
upload

PySide2 app
SQLite
catalog page
async API
download
local library
playback
play
pause/continue
stop
seek
playlist
manual reorder
shuffle
loop
client upload
client seed
persistence
no UI freeze
```

---

## P1 — Engineering Quality

After all P0 items work:

```text
tests
logging
error handling
performance measurement
memory testing
API documentation
type hints
lint
diagrams
documentation
```

---

## P2 — Optional Bonus

Only implement if P0 and P1 are stable.

Possible features:

```text
similar tracks
recommend next track
2D visualizer
3D visualizer
loop-one
download cancellation
```

Do NOT sacrifice mandatory stability for bonus features.

---

# 50. Similar Track Bonus

If implemented, keep it simple and explainable.

Example score:

```text
score =
    genre_match * 3
  + artist_match * 2
  + tag_similarity
```

No machine-learning model is required.

The goal is to demonstrate engineering judgment, not feature quantity.

---

# 51. Implementation Order

Codex MUST implement in this order unless a technical dependency requires adjustment.

```text
01. Initialize repository
02. Add .gitignore
03. Add Docker Compose PostgreSQL
04. Initialize FastAPI
05. Add /health
06. Add SQLAlchemy DB layer
07. Add Track model
08. Add FMA seed for 10 tracks
09. Add track list API
10. Add pagination
11. Add search
12. Add download
13. Add upload
14. Add server tests
15. Seed 100 tracks and verify
16. Initialize PySide2 client
17. Add SQLite
18. Add MainWindow/navigation
19. Add catalog QTableView
20. Add QAbstractTableModel
21. Add ApiClient
22. Add CatalogWorker/QThread
23. Add search debounce
24. Add DownloadWorker
25. Add atomic local downloads
26. Add Library page
27. Add PlaybackService
28. Add player widget
29. Add play/pause/stop
30. Add seek
31. Add playlist persistence
32. Add playlist UI
33. Add drag/drop reorder
34. Add PlaybackQueue
35. Add shuffle
36. Add loop
37. Add UploadWorker
38. Add upload UI
39. Add client seed
40. Add error handling
41. Add logging
42. Add hard-kill tests
43. Seed all 8,000 tracks
44. Benchmark startup
45. Test memory stability
46. Fix performance issues
47. Complete README
48. Complete DESIGN.md
49. Complete AGENTS.md
50. Complete SKILLS.md
51. Add all required diagrams
52. Final integration test
```

---

# 52. Five-Day Execution Plan

## Day 1

Goal:

Backend foundation.

Tasks:

```text
Repository
Docker
PostgreSQL
FastAPI
Track model
FMA parser
FMA seed
List API
Search
Pagination
```

End-of-day acceptance:

```bash
docker compose up
```

works and:

```http
GET /health
GET /api/v1/tracks
GET /api/v1/tracks?q=rock
```

work.

---

## Day 2

Goal:

Complete mandatory backend and start client.

Tasks:

```text
Download API
Upload API
Backend tests
PySide2 shell
SQLite
Catalog page
ApiClient
CatalogWorker
```

End-of-day acceptance:

Desktop client can display server catalog without freezing.

---

## Day 3

Goal:

Core music playback.

Tasks:

```text
DownloadWorker
local library
QMediaPlayer
play
pause/continue
stop
seek
```

End-of-day acceptance:

```text
server catalog
   ↓
download
   ↓
local library
   ↓
play locally
```

must work.

---

## Day 4

Goal:

Playlist and reliability.

Tasks:

```text
playlist create
add/remove
manual reorder
shuffle
loop
client upload
persistence
hard-kill testing
thread cleanup
error handling
```

End-of-day acceptance:

After `kill -9`, playlist and downloaded library state remain valid.

---

## Day 5

Goal:

Quality and submission.

Tasks:

```text
full 8000-track seed
startup benchmark
memory tests
unit tests
lint
README
DESIGN
AGENTS
SKILLS
diagrams
demo preparation
```

Do NOT add large new features unless everything mandatory is stable.

---

# 53. Definition of Done — Server

All MUST pass:

- [ ] `docker compose up --build` works.
- [ ] PostgreSQL starts successfully.
- [ ] API waits for healthy DB.
- [ ] `/health` works.
- [ ] FMA seed works.
- [ ] `--limit` seed works.
- [ ] Full dataset seed works.
- [ ] Catalog listing works.
- [ ] Search works.
- [ ] Pagination works.
- [ ] Download works.
- [ ] Upload works.
- [ ] Missing files return controlled errors.
- [ ] Swagger/OpenAPI works.
- [ ] Server tests pass.

---

# 54. Definition of Done — Client

All MUST pass:

- [ ] virtualenv setup is documented.
- [ ] PySide2 application starts.
- [ ] server catalog browses successfully.
- [ ] server catalog search works.
- [ ] pagination works.
- [ ] HTTP does not block UI.
- [ ] download runs in worker.
- [ ] download progress is visible.
- [ ] local library persists in SQLite.
- [ ] local track plays.
- [ ] pause/continue works.
- [ ] stop works.
- [ ] seek works.
- [ ] playlist creation works.
- [ ] add/remove tracks works.
- [ ] manual reorder works.
- [ ] reorder persists immediately.
- [ ] shuffle works.
- [ ] shuffle does not destroy persistent order.
- [ ] loop works.
- [ ] upload runs in worker.
- [ ] client seed works.
- [ ] failures do not crash application.

---

# 55. Definition of Done — Non-Functional

All MUST pass:

- [ ] Full FMA Small scale is tested.
- [ ] Startup < 10 seconds.
- [ ] UI remains responsive.
- [ ] No major memory growth during normal repeated use.
- [ ] `kill -9` does not lose committed playlist data.
- [ ] completed downloads survive restart.
- [ ] incomplete downloads are not registered as complete.
- [ ] no 8,000-row QWidget construction.
- [ ] no full audio-file buffering in memory.
- [ ] QThreads/workers are cleaned up.

---

# 56. Definition of Done — Documentation

All MUST exist:

- [ ] root README.md
- [ ] server/README.md
- [ ] client/README.md
- [ ] DESIGN.md
- [ ] AGENTS.md
- [ ] SKILLS.md
- [ ] context diagram
- [ ] container/C4 diagram
- [ ] server component diagram
- [ ] client component diagram
- [ ] ERD
- [ ] download sequence
- [ ] upload sequence
- [ ] playback sequence

---

# 57. Codex Coding Rules

Codex MUST follow these rules while implementing.

## Rule 1 — Keep the application runnable

After each major change:

- run relevant tests;
- verify application startup;
- avoid leaving repository in a broken state.

---

## Rule 2 — Do not over-engineer

Do NOT introduce:

- microservices;
- Kubernetes;
- Redis;
- Kafka;
- Celery;
- authentication frameworks;
- cloud infrastructure;

unless strictly required.

They are outside assignment scope.

---

## Rule 3 — Avoid premature bonus features

Do not implement:

- recommendation;
- visualizer;
- advanced themes;

until all mandatory features and reliability requirements pass.

---

## Rule 4 — Prefer simple explainable design

The implementation must be easy to defend in an interview.

Every major architecture choice should have a clear reason.

Examples:

```text
REST:
simple request/response operations.

SQLite:
embedded persistent local storage.

QThread:
avoid blocking Qt event loop.

QTableView:
efficient rendering for thousands of records.

PostgreSQL metadata + filesystem audio:
avoid storing large binary audio inside relational DB.
```

---

## Rule 5 — Type Hint Public Interfaces

Add type hints to:

- service methods;
- repository methods;
- worker constructors;
- important data structures.

Avoid spending excessive time typing trivial UI glue code.

---

## Rule 6 — Validate External Inputs

Validate:

- page/page_size;
- track ID;
- uploaded extension/content where practical;
- file existence;
- seed paths;
- database state.

---

## Rule 7 — Safe File Operations

For uploads/downloads:

```text
temporary file
   ↓
successful complete write
   ↓
atomic rename
   ↓
database commit
```

Never register a track before the file is safely available.

---

## Rule 8 — No Silent Exceptions

Do not use:

```python
try:
    ...
except Exception:
    pass
```

Log errors and surface recoverable errors to the user.

---

# 58. Interview Topics to Prepare

The implementation SHOULD make these questions easy to answer.

## Desktop event flow

Be able to explain:

```text
user click
   ↓
Qt signal
   ↓
worker starts
   ↓
network/file operation
   ↓
worker signal
   ↓
main-thread UI update
```

---

## Time Complexity

Examples:

Search query:

```text
without indexes:
potential O(N) scan
```

Pagination prevents all results from being transferred/rendered.

Playlist next:

```text
O(1)
```

Playlist reorder persistence:

```text
O(N)
```

for rewriting positions in a playlist, which is acceptable for normal playlist sizes.

---

## Reliability

Explain:

- immediate SQLite commits;
- atomic file rename;
- PostgreSQL persistence;
- worker error handling;
- `.part` download strategy;
- hard-kill testing.

---

## Trade-Offs

Be able to explain:

### REST vs WebSocket

REST chosen because mandatory features are request/response based.

### Filesystem vs PostgreSQL binary audio

Filesystem keeps DB smaller and simplifies file serving.

### SQLite client

Zero-admin embedded local persistence.

### Qt Model/View

Avoid thousands of widgets and improve memory/startup behavior.

### QThread

Qt event loop must not block on network/file operations.

---

# 59. Explicitly Out of Scope

Do NOT spend significant effort on:

- OAuth;
- SSO;
- password reset;
- production authentication;
- social features;
- lyrics;
- podcasts;
- radio;
- DRM;
- cloud deployment;
- cross-platform support;
- pixel-perfect Spotify clone;
- custom icon systems.

Ubuntu-only is acceptable.

---

# 60. Final Demo Script

Prepare a demo shorter than five minutes.

Recommended sequence:

```text
00:00  Start Docker Compose
00:20  Show server health/API docs
00:35  Start desktop client
00:50  Browse catalog
01:05  Search tracks
01:20  Download a track
01:45  Play downloaded track
02:00  Pause/continue
02:15  Seek
02:30  Create playlist
02:45  Add/reorder tracks
03:05  Shuffle
03:20  Loop
03:35  Upload a local track
04:00  Hard kill client
04:10  Restart client
04:20  Show persistent playlist/library
04:35  Briefly show architecture/docs/tests
```

---

# 61. Final Submission Checks

Before submission:

- repository is private;
- correct collaborator is invited;
- main branch contains real commit history;
- no FMA dataset is committed;
- no large accidental binary files are committed;
- README instructions were tested on a clean environment;
- video is below required duration;
- email contains:
  - repository link;
  - approximate time spent;
  - video link.

---

# 62. Codex Execution Instructions

When Codex works on this repository, follow this workflow:

1. Read this file completely.
2. Read `README.md`, `DESIGN.md`, `AGENTS.md`, and `SKILLS.md` if they exist.
3. Inspect the current repository before changing files.
4. Determine the next incomplete task from Section 51.
5. Implement the smallest complete vertical increment.
6. Run tests/verification relevant to the increment.
7. Fix failures before moving forward.
8. Keep code simple and interview-explainable.
9. Preserve existing working behavior.
10. Update documentation when architecture or setup changes.
11. Do not implement P2 work while any P0 requirement is incomplete.
12. Never block the Qt UI thread with network or heavy file operations.
13. Never commit the FMA dataset.
14. Keep real Git history with meaningful commits.
15. At the end, verify every Definition of Done checklist.

---

# 63. First Codex Task

If the repository is empty, begin with:

```text
Task 1:
Initialize the repository structure exactly as described in this specification.

Then implement:
- .gitignore
- root README skeleton
- docker-compose.yml
- server FastAPI skeleton
- PostgreSQL connection
- /health endpoint
- Dockerfile
- initial server tests

Verify:
docker compose up --build

Then verify:
GET http://localhost:8000/health

Expected:
{"status":"ok"}
```

Do not proceed to the desktop client until the server foundation is working.

---

# 64. Completion Principle

The project is successful when it is:

```text
correct
+
responsive
+
persistent
+
easy to run
+
easy to understand
+
easy to explain in an interview
```

Feature quantity is less important than completing the mandatory behavior with good reliability and engineering quality.
