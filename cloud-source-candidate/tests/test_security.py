import pytest
from fastapi import HTTPException

from security import validate_api_key


def test_rejects_when_server_key_is_not_configured():
    with pytest.raises(HTTPException) as error:
        validate_api_key("client-key", None)
    assert error.value.status_code == 503


def test_rejects_missing_client_key():
    with pytest.raises(HTTPException) as error:
        validate_api_key(None, "server-key")
    assert error.value.status_code == 401


def test_rejects_incorrect_client_key():
    with pytest.raises(HTTPException) as error:
        validate_api_key("wrong-key", "server-key")
    assert error.value.status_code == 401


def test_accepts_matching_client_key():
    assert validate_api_key("server-key", "server-key") is None


def test_dependency_rejects_missing_header(monkeypatch):
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from security import require_api_key

    monkeypatch.setenv("SHOPFAST_API_KEY", "server-key")
    app = FastAPI()

    @app.get("/protected")
    def protected(_auth: None = Depends(require_api_key)):
        return {"ok": True}

    response = TestClient(app).get("/protected")
    assert response.status_code == 401


def test_dependency_accepts_matching_header(monkeypatch):
    from fastapi import Depends, FastAPI
    from fastapi.testclient import TestClient
    from security import require_api_key

    monkeypatch.setenv("SHOPFAST_API_KEY", "server-key")
    app = FastAPI()

    @app.get("/protected")
    def protected(_auth: None = Depends(require_api_key)):
        return {"ok": True}

    response = TestClient(app).get(
        "/protected", headers={"X-API-Key": "server-key"}
    )
    assert response.status_code == 200
