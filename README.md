# Eureka Music

Eureka Music is a small Ubuntu-targeted music system with a FastAPI/PostgreSQL backend and a Python desktop client planned around PySide2, SQLite, background workers, and local playback.

## Architecture

- Server: FastAPI, SQLAlchemy, PostgreSQL, filesystem audio storage.
- Client: PySide2, SQLite, local downloaded files, Qt worker threads.
- Dataset: FMA Small, seeded from a local extracted dataset path.

## Prerequisites

- Docker and Docker Compose
- Python 3.10 recommended
- FMA Small dataset extracted locally for seeding

## Quick Start

```bash
docker compose up --build
```

Then open:

- Health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Seed Server

```bash
cd server
python seed.py /path/to/fma --limit 100
```

The server seed expects:

```text
fma/
  fma_small/
  fma_metadata/tracks.csv
```

## Start Client

```bash
cd client
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Run Tests

Run server and client suites separately because both projects intentionally use a top-level Python package named `app`.

```bash
python -m pytest server/tests
python -m pytest client/tests
```

## Performance Notes

The server uses paginated APIs so the client never has to fetch or render the full FMA catalog at once. Audio files are stored on disk, not in PostgreSQL.

Client network and file operations run in `QThread` workers. Local metadata is stored in SQLite and committed immediately after changes.

## Known Limitations

- Docker Compose verification requires Docker Desktop or Docker daemon to be running.
- The PySide2 client should be run with Python 3.10 on Ubuntu; PySide2 5.15.x is not intended for the newest Python releases.
- Authentication and cloud deployment are outside the assignment scope.

## Demo Flow

1. Start `docker compose up --build`.
2. Visit `/health` and `/docs`.
3. Seed a subset of FMA.
4. Browse/search `/api/v1/tracks`.
5. Download/upload a test audio file.
