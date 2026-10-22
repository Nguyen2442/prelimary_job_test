from fastapi import FastAPI

app = FastAPI(title="ksynerX API", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello from ksynerX"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
