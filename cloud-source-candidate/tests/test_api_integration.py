import importlib
import io
import sys
import types
import uuid

import joblib
import pytest
import zipfile
from fastapi.testclient import TestClient


@pytest.fixture(params=["api", "api_respaldo"])
def api_runtime(monkeypatch, request):
    """Load each real FastAPI app while replacing cloud services and model files."""
    module_name = request.param
    sys.modules.pop(module_name, None)

    published_events = []

    sagemaker = types.ModuleType("sagemaker_cliente")
    sagemaker.predecir_aws = lambda rows: [0.8] * len(rows)

    messaging = types.ModuleType("mensajeria")
    messaging.publicar_evento = lambda event: published_events.append(event)

    monkeypatch.setitem(sys.modules, "sagemaker_cliente", sagemaker)
    monkeypatch.setitem(sys.modules, "mensajeria", messaging)

    pika = types.ModuleType("pika")
    pika.exceptions = types.SimpleNamespace(
        AMQPError=type("AMQPError", (Exception,), {})
    )
    monkeypatch.setitem(sys.modules, "pika", pika)

    class FakePipeline:
        def predict_proba(self, frame):
            import numpy as np
            return np.array([[0.2, 0.8] for _ in range(len(frame))])

    monkeypatch.setattr(
        joblib,
        "load",
        lambda _path: {
            "features": ["usuario", "contexto", "coincide"],
            "pipeline": FakePipeline(),
        },
    )

    class FakeArchive:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def open(self, _name):
            csv = (
                "producto,categoria\n"
                "P17,audio\n"
                "P28,video\n"
            )
            return io.BytesIO(csv.encode("utf-8"))

    monkeypatch.setattr(zipfile, "ZipFile", lambda *_args, **_kwargs: FakeArchive())
    monkeypatch.setenv("SHOPFAST_API_KEY", "integration-test-key")

    api = importlib.import_module(module_name)
    try:
        yield api, published_events
    finally:
        sys.modules.pop(module_name, None)


@pytest.fixture
def client(api_runtime):
    api, _published = api_runtime
    return TestClient(api.app)


def test_real_recommendations_route_rejects_missing_key(client):
    response = client.get("/v1/recommendations?subject_ref=U7")
    assert response.status_code == 401


def test_real_recommendations_route_rejects_wrong_key(client):
    response = client.get(
        "/v1/recommendations?subject_ref=U7",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_real_recommendations_route_accepts_valid_key(client):
    response = client.get(
        "/v1/recommendations?subject_ref=U7&context=audio&limit=5",
        headers={"X-API-Key": "integration-test-key"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["items"]
    assert body["items"][0]["product_id"] == "P17"


def make_event():
    return {
        "event_id": str(uuid.uuid4()),
        "source": "web",
        "type": "click",
        "subject_ref": "U7",
        "product_id": "P17",
        "occurred_at": "2026-11-27T12:00:00+00:00",
        "schema_version": 1,
        "recommendation_id": "integration-test",
    }


def test_real_events_route_rejects_missing_key(client):
    response = client.post("/v1/events", json=make_event())
    assert response.status_code == 401


def test_real_events_route_rejects_wrong_key(client):
    response = client.post(
        "/v1/events",
        json=make_event(),
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_real_events_route_accepts_valid_key_and_publishes(api_runtime):
    api, published = api_runtime
    client = TestClient(api.app)
    event = make_event()

    response = client.post(
        "/v1/events",
        json=event,
        headers={"X-API-Key": "integration-test-key"},
    )

    assert response.status_code == 202
    assert response.json()["event_id"] == event["event_id"]
    assert response.json()["queue"] == "shopfast.events"
    assert len(published) == 1
    assert published[0]["event_id"] == event["event_id"]


def test_events_route_returns_503_when_broker_is_unavailable(api_runtime, monkeypatch):
    api, _published = api_runtime
    client = TestClient(api.app)

    def unavailable(_event):
        raise OSError("broker unavailable")

    monkeypatch.setattr(api, "publicar_evento", unavailable)
    response = client.post(
        "/v1/events",
        json=make_event(),
        headers={"X-API-Key": "integration-test-key"},
    )

    assert response.status_code == 503
