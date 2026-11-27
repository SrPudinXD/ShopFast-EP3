from locust import HttpUser, task, between
from pathlib import Path
import os

env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
API_KEY = os.getenv("SHOPFAST_API_KEY")
if not API_KEY:
    raise RuntimeError("Define SHOPFAST_API_KEY en entorno o .env local no versionado.")

class ShopFastUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def recomendaciones(self):
        with self.client.get("/v1/recommendations",
            params={"subject_ref": "U999", "context": "audio", "limit": 10, "surface": "home"},
            headers={"X-API-Key": API_KEY}, name="GET /v1/recommendations",
            catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
                return
            try:
                data = response.json()
            except Exception:
                response.failure("JSON inválido")
                return
            if data.get("fallback") is True:
                response.failure("Se activó fallback")
            elif not data.get("items"):
                response.failure("Respuesta sin recomendaciones")
            else:
                response.success()