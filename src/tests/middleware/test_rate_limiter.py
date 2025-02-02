import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.middleware.rate_limiter import RateLimiter
import time

app = FastAPI()
app.middleware("http")(RateLimiter())

@app.get("/test-rate")
async def test_rate():
    return {"status": "ok"}

client = TestClient(app)

def test_rate_limiter():
    # Test within limits
    for _ in range(100):
        response = client.get("/test-rate")
        assert response.status_code == 200

    # Test exceeding limits
    response = client.get("/test-rate")
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}
