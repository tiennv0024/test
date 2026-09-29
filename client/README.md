# Eureka Music Client

Python/PySide2 desktop client for Eureka Music.

## Setup

```bash
cd client
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

The client expects the server at `http://localhost:8000` by default. Override with:

```bash
export EUREKA_SERVER_URL=http://localhost:8000
```

## Seed Local Library

```bash
python seed.py /path/to/fma --limit 100
```

Local application data is stored under `~/.local/share/eureka-music/`.
