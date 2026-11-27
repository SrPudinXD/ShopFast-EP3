from pydantic import BaseModel
from fastapi import HTTPException, FastAPI, Query, Depends
from datetime import datetime
from mensajeria import publicar_evento
import pika
from pathlib import Path
from uuid import uuid4
from time import time
from threading import Lock
import zipfile
import joblib
import pandas as pd
from typing import Literal
from security import require_api_key

ROOT = Path(__file__).resolve().parent
artifact = joblib.load(ROOT / "modelo.joblib")
with zipfile.ZipFile(ROOT / "ShopFast_datos.zip") as archive:
    catalog = pd.read_csv(archive.open("catalogo.csv"))

app = FastAPI(title="ShopFast EP3 - respaldo local", version="0.1.0")
lock = Lock()
stock = {}


def apply_stock(product, revision, units, observed_at, active=True, eligible=True):
    with lock:
        previous = stock.get(product)
        if previous is not None and revision <= previous["revision"]:
            return False
        stock[product] = dict(
            revision=revision, units=units, observed_at=observed_at,
            active=active, eligible=eligible
        )
        return True


# Inventario simulado del incidente; no es una conexión comercial real.
for product, units in [("P17", 8), ("P28", 6)]:
    apply_stock(product, 40, units, time())


def recommendations(subject, context, limit, now):
    with lock:
        snapshot = {product: dict(item) for product, item in stock.items()}
    excluded = {}
    valid = []
    for product in catalog.producto:
        item = snapshot.get(product)
        reason = (
            "inventory_unknown" if item is None else
            "inventory_expired" if not 0 <= now - item["observed_at"] <= 300 else
            "out_of_stock" if item["units"] <= 0 else
            "ineligible" if not item["active"] or not item["eligible"] else
            None
        )
        if reason:
            excluded[reason] = excluded.get(reason, 0) + 1
        else:
            valid.append(product)

    data = catalog[catalog.producto.isin(valid)].copy()
    data["usuario"] = subject
    data["contexto"] = context
    data["coincide"] = (data.contexto == data.categoria).astype(int)
    mode = "empty"
    items = []

    if not data.empty:
        try:
            data["score"] = artifact["pipeline"].predict_proba(
                data[artifact["features"]]
            )[:, 1]
            mode = "personalized"
        except Exception:
            data["score"] = data["coincide"]
            mode = "alternative"

        data = data.sort_values(
            ["score", "producto"], ascending=[False, True]
        ).head(limit)
        items = [
            {"product_id": row.producto, "score": float(row.score)}
            for row in data.itertuples()
        ]

    return {
        "recommendation_id": str(uuid4()),
        "model_version": "rf-local-v1" if mode == "personalized" else None,
        "mode": mode,
        "fallback": mode != "personalized",
        "items": items,
        "reason": (
            "inventory_unverified_or_unavailable" if not items else
            "model_unavailable" if mode == "alternative" else None
        ),
        "excluded": excluded,
        "inference_environment": "local",
        "inventory_environment": "simulated",
    }


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/v1/recommendations")
def get_recommendations(
    subject_ref: str = Query(min_length=1, max_length=80),
    context: Literal["audio", "video", "redes", "movil"] = "audio",
    limit: int = Query(10, ge=1, le=10),
    surface: Literal["home", "product"] = "home",
    _auth: None = Depends(require_api_key),
):
    result = recommendations(subject_ref, context, limit, time())
    result["surface"] = surface
    return result


class Evento(BaseModel):
    event_id: str
    source: Literal["web", "mobile"]
    type: Literal["click", "impression", "cart", "purchase"]
    subject_ref: str
    product_id: str
    occurred_at: datetime
    schema_version: Literal[1] = 1
    recommendation_id: str


@app.post("/v1/events", status_code=202)
def registrar_evento(evento: Evento, _auth: None = Depends(require_api_key)):
    try:
        publicar_evento(evento.model_dump(mode="json"))
        return {
            "status": "accepted",
            "event_id": evento.event_id,
            "broker": "RabbitMQ",
            "queue": "shopfast.events",
        }
    except (pika.exceptions.AMQPError, OSError, KeyError):
        raise HTTPException(
            status_code=503,
            detail="Servicio de mensajeria no disponible",
        )
