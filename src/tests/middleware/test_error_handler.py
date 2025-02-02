import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from src.middleware.error_handler import ErrorHandler

app = FastAPI()
app.middleware("http")(ErrorHandler())

@app.get("/test-error")
async def test_error():
    raise HTTPException(status_code=500, detail="Test error")

@app.get("/test-validation")
async def test_validation():
    raise ValidationError("Invalid data")

client = TestClient(app)

def test_error_handler_internal_error():
    response = client.get("/test-error")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

def test_error_handler_validation_error():
    response = client.get("/test-validation")
    assert response.status_code == 422
    assert "detail" in response.json()
