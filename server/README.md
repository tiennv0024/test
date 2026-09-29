# Eureka Music Server

FastAPI backend for Eureka Music.

## Run With Docker

```bash
docker compose up --build
```

## Local Development

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://eureka:eureka@localhost:5432/eureka_music
uvicorn app.main:app --reload
```

## Seed FMA Small

```bash
python seed.py /path/to/fma --limit 100
```

## API

- `GET /health`
- `GET /api/v1/tracks?page=1&page_size=50&q=rock`
- `GET /api/v1/tracks/{track_id}`
- `GET /api/v1/tracks/{track_id}/download`
- `POST /api/v1/tracks`
