<!-- fullWidth: false tocVisible: false tableWrap: true -->
# prelimary job test API

FastAPI project managed with [uv](https://docs.astral.sh/uv/).

## Run locally

```bash
uv sync
uv run fastapi dev app/main.py
```

Open http://localhost:8000/docs

## Run with Docker

```bash
docker compose up --build
```

## Add dependencies

```bash
uv add <package>          # dependency
uv add --dev <package>    # dev dependency
```