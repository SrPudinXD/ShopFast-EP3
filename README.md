# ShopFast EP3 — ITY1102

Equipo: Javier Moyano, Alvaro Prieto y Martin Torres.

## Alcance
Arquitectura documentada: Random Forest, FastAPI, AWS SageMaker, EC2, RabbitMQ, Redis y dashboard. El inventario es simulado; no existe integración comercial ni reserva de stock.

**Brecha importante:** el código completo desplegado en EC2 (/home/ubuntu/shopfast) no estaba en los archivos recuperados. El prototipo local disponible no tiene autenticación, TLS, broker ni persistencia duradera. No se presenta como código cloud. Ver [docs/cloud-source-gap.md](docs/cloud-source-gap.md).

## Estructura
- prototype-local/: API y pruebas del prototipo local.
- model/: entrenamiento y métricas.
- load-test/: script Locust y resultados.
- docs/: arquitectura, rúbrica, evidencias y acceso AWS.
- Dockerfile: prototipo local, no el original EC2.
- docker-compose.yml: RabbitMQ/Redis locales de laboratorio.

## Entrenamiento
Extraer ShopFast_datos.zip del adjunto de Anexo_Evaluacion3.pdf a model/ShopFast_datos.zip:
```bash
pip install -r model/requirements.txt
python model/entrenar.py
```
Copiar model/modelo.joblib y model/ShopFast_datos.zip a prototype-local/.

## Prototipo local
Requiere Python 3.12, prototype-local/modelo.joblib y prototype-local/ShopFast_datos.zip:
```bash
pip install -r prototype-local/requirements.txt
cd prototype-local
python probar.py
uvicorn api:app --host 127.0.0.1 --port 8000
```
Swagger: http://127.0.0.1:8000/docs. No exponer a Internet.

## Docker
Tras copiar ambos artefactos a prototype-local/:
```bash
docker build -t shopfast-prototype .
docker run --rm -p 127.0.0.1:8000:8000 -v "$PWD/prototype-local/modelo.joblib:/app/modelo.joblib:ro" -v "$PWD/prototype-local/ShopFast_datos.zip:/app/ShopFast_datos.zip:ro" shopfast-prototype
```
RabbitMQ/Redis locales: definir RABBITMQ_DEFAULT_PASS en .env local no versionado y ejecutar docker compose up -d. La API local no publica eventos a estos servicios.

## Locust documentado
10 usuarios, incremento 2 usuarios/s, 60 s, EC2 loopback 127.0.0.1:8000. CSV: 382 solicitudes, 0 fallos, 6,47 req/s, media 37,7 ms, P95 45 ms, P99 110 ms, máximo 161 ms. La consola indicó 386 solicitudes. No demuestra 250/750 req/s ni latencia desde Internet. Ver load-test/Resultados_Locust_LEER.md.

## Seguridad
No subir .env, API Keys, claves PEM, contraseñas ni credenciales AWS. Una captura con API Key fue excluida; rotarla si sigue vigente.

Informe PDF de 10 páginas, DOCX editable, presentación PDF de 6 láminas, PPTX y 305 capturas sanitizadas permanecen en el paquete AVA. La conexión GitHub usada permite crear archivos de texto; los binarios no están incluidos en este commit.