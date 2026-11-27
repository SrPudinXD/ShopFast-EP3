# Revisión técnica propuesta — ShopFast cloud

## Alcance

Esta revisión se realizó sobre los snapshots sanitizados de API, Dashboard, unidades systemd, configuración y dependencias recuperados desde EC2. Los cambios se mantienen en la rama `review/cloud-hardening`; la rama `main` conserva el snapshot previo para no confundir correcciones propuestas con código que estaba desplegado.

## Hallazgos y correcciones

| Hallazgo en el snapshot | Riesgo o efecto | Corrección propuesta |
|---|---|---|
| API acepta `X-API-Key` en las llamadas de prueba, pero no valida la cabecera | Las pruebas no acreditan autenticación efectiva | Añadir `security.py` y validar `SHOPFAST_API_KEY` en recomendaciones y eventos |
| Dashboard registra dos veces `/api/recomendaciones` | Registro duplicado de la misma ruta y ruido en OpenAPI | Dejar un único decorador |
| Dashboard no contempla JSON inválido del motor interno | Una respuesta no JSON puede terminar como error 500 | Convertir `ValueError` en respuesta controlada 503 |
| No había un archivo pequeño de dependencias runtime derivado del entorno EC2 | Difícil distinguir dependencias de servicio de un `pip freeze` completo | Añadir `requirements-runtime-ec2-snapshot.txt` con dependencias directas y versiones observadas |
| La API y el Dashboard leen secretos desde el entorno | Requiere configuración fuera de Git | Añadir `SHOPFAST_API_KEY` como marcador en `env.example`, nunca un secreto real |

## Contrato de autenticación propuesto

- `GET /health/live`: público, para comprobación de vida del proceso.
- `GET /v1/recommendations`: requiere `X-API-Key` en `api.py` y `api_respaldo.py`.
- `POST /v1/events`: requiere `X-API-Key` en `api.py` y `api_respaldo.py`.
- La clave esperada se lee desde `SHOPFAST_API_KEY`.
- Si el servidor no tiene la clave configurada, devuelve HTTP 503.
- Si falta la cabecera o no coincide, devuelve HTTP 401.
- La comparación se realiza con `hmac.compare_digest`.
- El Dashboard llama al endpoint de recomendaciones desde el backend y no envía la clave al navegador.

La ruta `GET /api/dashboard` del Dashboard no tiene autenticación propia en el código revisado. Debe permanecer enlazada a `127.0.0.1` y accesible solo mediante el túnel SSH autorizado; no publicarla directamente.

## Pruebas realizadas

Se ejecutaron seis pruebas unitarias y de dependencia aislada sobre el validador de clave:

1. Falta la clave del servidor → HTTP 503.
2. Falta la clave del cliente → HTTP 401.
3. La clave del cliente es incorrecta → HTTP 401.
4. La clave coincide → validación correcta.
5. La dependencia FastAPI rechaza una petición sin cabecera → HTTP 401.
6. La dependencia FastAPI acepta una petición con cabecera correcta → HTTP 200.

**Resultado:** 6 pruebas aprobadas en el entorno local de revisión (Python 3.13.5, FastAPI 0.128.2 y pytest 9.0.2). Esto valida el helper y la dependencia en una app FastAPI mínima; no es una prueba integrada de los módulos ShopFast en Python 3.12.3 de EC2.

Las pruebas se ejecutaron en el entorno disponible (Python 3.13.5, FastAPI 0.128.2, HTTPX 0.28.1 y pytest 9.0.2). El archivo de pruebas fija FastAPI 0.165.0, HTTPX 0.28.1 y pytest 9.2.0 para el entorno de prueba previsto. No se ejecutó la aplicación cloud completa ni una prueba integrada con SageMaker, Redis o RabbitMQ. Los binarios de modelo y dataset no están versionados, y no se verificó el estado actual de EC2.

## Compatibilidad de dependencias

El entorno de entrenamiento registra NumPy 2.3.5, pandas 2.2.3 y joblib 1.5.3. El snapshot de EC2 registra NumPy 2.5.5, pandas 3.1.1 y joblib 1.6.0. Scikit-learn aparece como 1.8.0 en ambos.

Antes de desplegar:
- Cargar el artefacto `modelo.joblib` exacto con el entorno objetivo.
- Ejecutar la API con el dataset real en una instancia de staging.
- Comprobar inferencia local y SageMaker.
- Probar acceso autorizado y rechazo de claves incorrectas.
- Verificar el flujo de evento hasta Redis y Dashboard.
- Comparar los archivos desplegados con el commit aprobado.

No actualizar producción directamente desde esta rama sin completar estas comprobaciones.

## Archivos de la rama

- `cloud-source-candidate/security.py`
- `cloud-source-candidate/api.py`
- `cloud-source-candidate/api_respaldo.py`
- `cloud-source-candidate/dashboard_api.py`
- `cloud-source-candidate/env.example`
- `cloud-source-candidate/requirements-runtime-ec2-snapshot.txt`
- `cloud-source-candidate/requirements-test.txt` (FastAPI, HTTPX y pytest)
- `cloud-source-candidate/tests/test_security.py`
