from fastapi.testclient import TestClient
from api import app, stock, apply_stock, recommendations
import json
from time import time

client = TestClient(app)
stock.clear()
now = time()
apply_stock("P17", 40, 8, now)
apply_stock("P28", 40, 6, now)
results = []


def check(name, condition):
    assert condition, name
    results.append({"prueba": name, "resultado": "OK"})
    print("OK:", name)


response = client.get(
    "/v1/recommendations",
    params={"subject_ref": "U7", "context": "audio"},
)
print(response.json())
check(
    "HTTP 200 e inferencia con fallback local disponible",
    response.status_code == 200
    and response.json()["mode"] == "personalized",
)
check(
    "Solo inventario conocido",
    {item["product_id"] for item in response.json()["items"]}
    == {"P17", "P28"},
)
check(
    "Limite solicitado",
    len(client.get(
        "/v1/recommendations",
        params={"subject_ref": "U7", "limit": 1},
    ).json()["items"]) == 1,
)
check(
    "Limite invalido",
    client.get(
        "/v1/recommendations",
        params={"subject_ref": "U7", "limit": 11},
    ).status_code == 422,
)
apply_stock("P17", 42, 0, now + 7)
check(
    "Stock cero excluido",
    [item["product_id"] for item in recommendations(
        "U7", "audio", 10, now + 8
    )["items"]] == ["P28"],
)
check(
    "Revision antigua rechazada",
    not apply_stock("P17", 41, 4, now + 5),
)
check(
    "Revision 42 conservada",
    stock["P17"]["units"] == 0 and stock["P17"]["revision"] == 42,
)
check(
    "Inventario vencido devuelve lista vacia",
    recommendations("U8", "audio", 10, now + 315)["items"] == [],
)
check(
    "Usuario nuevo admitido",
    recommendations("U_NEW", "audio", 10, now + 8)["mode"]
    == "personalized",
)
check("Health live", client.get("/health/live").status_code == 200)

with open("pruebas_locales.json", "w", encoding="utf-8") as output:
    json.dump(results, output, indent=2, ensure_ascii=False)
