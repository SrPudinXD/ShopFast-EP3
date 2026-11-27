import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from fastapi import HTTPException
from time import perf_counter
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from datetime import datetime, timezone
import redis
import json

app = FastAPI(
    title="ShopFast Analytics",
    version="2.0.0"
)

ROOT = Path(__file__).resolve().parent

almacen = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3
)


@app.get("/api/dashboard")
def obtener_indicadores():

    eventos = None

    distribucion = {
        "click": 0,
        "impression": 0,
        "cart": 0,
        "purchase": 0
    }

    productos = {}

    try:
        redis_activo = almacen.ping()
        eventos = 0

        for clave in set(almacen.scan_iter(match="evento:*")):

            contenido = almacen.get(clave)

            if not contenido:
                continue

            evento = json.loads(contenido)
            eventos += 1

            tipo = evento.get("type")
            producto = evento.get("product_id")

            if tipo in distribucion:
                distribucion[tipo] += 1

            if producto:
                productos[producto] = productos.get(
                    producto, 0
                ) + 1

    except (redis.RedisError, ValueError):
        redis_activo = False
        eventos = None
        distribucion = None
        productos = None

    return {
        "proyecto": "ShopFast EP3",
        "entorno": "AWS Cloud",
        "eventos_registrados": eventos,
        "redis": redis_activo,
        "dashboard": "operativo",
        "modelo_configurado": "Random Forest",
        "inventario": "simulado",
        "distribucion_eventos": distribucion,
        "interacciones_productos": productos,
        "actualizacion": datetime.now(
            timezone.utc
        ).isoformat()
    }


@app.get("/api/recomendaciones")
def obtener_recomendaciones():

    clave = os.getenv("SHOPFAST_API_KEY")

    if not clave:
        raise HTTPException(
            status_code=503,
            detail="Autenticacion no configurada"
        )

    url = (
        "http://127.0.0.1:8000/v1/recommendations"
        "?subject_ref=U7&context=audio&limit=5&surface=home"
    )

    solicitud = Request(
        url,
        headers={"X-API-Key": clave}
    )

    inicio = perf_counter()

    try:
        with urlopen(solicitud, timeout=15) as respuesta:
            datos = json.load(respuesta)

        datos["latencia_ms"] = round(
            (perf_counter() - inicio) * 1000, 2
        )

        datos["cantidad_productos"] = len(
            datos.get("items", [])
        )

        return datos

    except (HTTPError, URLError, TimeoutError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Motor de recomendaciones no disponible"
        )

app.mount(
    "/",
    StaticFiles(
        directory=str(ROOT / "dashboard"),
        html=True
    ),
    name="dashboard"
)
