# Revisión técnica propuesta — ShopFast cloud

## Alcance

Esta revisión se realizó sobre los snapshots sanitizados de API, Dashboard, unidades systemd, configuración y dependencias recuperados desde EC2. Los cambios de endurecimiento se mantienen en la rama `review/cloud-hardening`; la rama `main` conserva el snapshot previo para distinguir las correcciones propuestas del código recuperado.

## Hallazgos y correcciones propuestas

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

## Pruebas automatizadas de la rama

Se ejecutaron seis pruebas unitarias y de dependencia aislada sobre el validador de clave:

1. Falta la clave del servidor → HTTP 503.
2. Falta la clave del cliente → HTTP 401.
3. La clave del cliente es incorrecta → HTTP 401.
4. La clave coincide → validación correcta.
5. La dependencia FastAPI rechaza una petición sin cabecera → HTTP 401.
6. La dependencia FastAPI acepta una petición con cabecera correcta → HTTP 200.

**Workflow GitHub Actions:** se añadió `.github/workflows/tests.yml` para ejecutar `python -m pytest -q tests/` en Python 3.12 en los eventos `push` de `main`/`review/cloud-hardening` y `pull_request` hacia `main`. La ejecución remota del 27-11-2026 en el commit `5583724e5a34870f7d3a4d87fb0042ebb16ab2ad` terminó correctamente: `13 passed` en Python 3.12. Incluye seis pruebas unitarias/de dependencia y siete pruebas de integración de las rutas reales de FastAPI, con AWS, RabbitMQ y artefactos del modelo aislados mediante dobles de prueba. No sustituye las pruebas en EC2 con servicios reales.

**Resultado histórico:** 6 pruebas unitarias/de dependencia aprobadas en la primera ejecución del workflow. Se añadieron después pruebas de integración de las rutas reales de FastAPI; su resultado remoto está pendiente de la nueva ejecución de GitHub Actions. en el entorno local de revisión (Python 3.13.5, FastAPI 0.128.2, HTTPX 0.28.1 y pytest 9.0.2). El archivo `requirements-test.txt` fija FastAPI 0.165.0, HTTPX 0.28.1 y pytest 9.2.0 para el entorno de prueba previsto. Estas pruebas validan el helper y la dependencia en una aplicación FastAPI mínima; no son pruebas de integración de las rutas ShopFast ni acreditan que esta rama esté desplegada en EC2.

## Validación runtime observada en EC2 — 27-11-2026

Las siguientes comprobaciones se ejecutaron sobre la instancia EC2 existente, antes de desplegar las modificaciones de esta rama:

| Componente o prueba | Resultado observado |
|---|---|
| Python del entorno virtual | 3.12.3 |
| NumPy / pandas / joblib / scikit-learn | 2.5.5 / 3.1.1 / 1.6.0 / 1.8.0 |
| `pip check` | Sin dependencias rotas |
| `modelo.joblib` | Carga correcta; pipeline Random Forest y 6 características |
| `ShopFast_datos.zip` | ZIP íntegro; `catalogo.csv` e `impresiones.csv` presentes |
| Inferencia local | 5 predicciones ejecutadas sin error |
| SageMaker | Endpoint `shopfast-endpoint-v1` en `InService`, región `us-east-2` |
| Inferencia SageMaker | 3 predicciones correctas; coincidieron con los resultados locales para las mismas entradas |
| API | `GET /health/live` devolvió HTTP 200 |
| Dashboard | `GET /api/dashboard` devolvió HTTP 200 |
| Redis | `PING` respondió `PONG`; claves `evento:*` detectadas |
| RabbitMQ | Diagnóstico de conexión correcto; cola `shopfast.events` |
| Consumidor | Servicio systemd activo; 1 consumidor; al finalizar, 0 mensajes ready y 0 unacknowledged |
| Flujo de evento | Publicación controlada confirmada por RabbitMQ; el consumidor persistió el evento en Redis |
| Dashboard después de la prueba | 8 eventos registrados, `redis: true`, `dashboard: operativo` e interacción de producto P17 actualizada a 8 |

La prueba de inferencia SageMaker comparó tres resultados con los resultados locales correspondientes: P1 0.1189, P2 0.0591 y P3 0.0565. La prueba de mensajería publicó un evento de identificador único; el script comprobó su existencia en Redis y el Dashboard mostró el contador incrementado de 7 a 8.

**Límite importante:** estas pruebas acreditan el funcionamiento observado del entorno EC2 existente y su flujo de inferencia/eventos. No prueban que los cambios de autenticación de `review/cloud-hardening` estén instalados en esa instancia. Tampoco sustituyen una prueba de autorización HTTP de las rutas protegidas, una comparación byte a byte de todos los archivos activos o una validación de despliegue de esta rama.


## Validación HTTP de autenticación en EC2 — 27-11-2026

Se inspeccionó el código activo de `api.py` y se comprobó que define `APIKeyHeader` para `X-API-Key`, obtiene el secreto desde `SHOPFAST_API_KEY`, utiliza `secrets.compare_digest` y protege las rutas de recomendaciones y eventos mediante la dependencia `verificar_api_key`. El health check permanece separado.

Se ejecutaron tres solicitudes HTTP reales contra `GET /v1/recommendations` en la instancia EC2:

| Escenario | Respuesta observada | Resultado |
|---|---:|---|
| Sin cabecera `X-API-Key` | HTTP 401 | Correcto |
| Cabecera con clave incorrecta | HTTP 401 | Correcto |
| Cabecera con clave configurada | HTTP 200 | Correcto |

La clave se leyó localmente desde `.env`; no se imprimió ni se incorporó a Git.

**Alcance:** esta prueba valida la autenticación de `GET /v1/recommendations` en el código que ya estaba desplegado en EC2. No valida todavía `POST /v1/events` por HTTP ni demuestra que los cambios de `review/cloud-hardening` estén desplegados. La rama contiene una implementación de seguridad separada; debe compararse y probarse contra el código activo antes de cualquier despliegue.


## Validación HTTP de autenticación de eventos en EC2 — 27-11-2026

Se ejecutaron tres solicitudes HTTP reales a `POST /v1/events` con el mismo payload válido y distinto encabezado de autenticación:

| Escenario | Respuesta observada | Resultado |
|---|---:|---|
| Sin cabecera `X-API-Key` | HTTP 401 | Correcto |
| Cabecera con clave incorrecta | HTTP 401 | Correcto |
| Cabecera con clave configurada | HTTP 202 | Correcto |

La solicitud autorizada fue aceptada para publicación en RabbitMQ y devolvió el identificador `bb713dc6-0923-4375-b71c-5cba51ae5a5c`. La clave se leyó localmente desde `.env`; no se imprimió ni se incorporó al repositorio.

En conjunto con las tres pruebas de `GET /v1/recommendations` documentadas anteriormente, hay seis escenarios HTTP correctos en el código desplegado en EC2: 401/401/200 para recomendaciones y 401/401/202 para eventos.

**Alcance pendiente:** HTTP 202 confirma que la API aceptó el evento para publicación; por sí solo no demuestra que este evento específico ya haya sido consumido y persistido en Redis. Debe verificarse por separado. Estas pruebas corresponden al código activo en EC2 y no acreditan el despliegue de la rama `review/cloud-hardening`.


## Confirmación de persistencia del evento autorizado — 27-11-2026

Se verificó el evento enviado por `POST /v1/events` después de recibir HTTP 202:

- Identificador: `bb713dc6-0923-4375-b71c-5cba51ae5a5c`.
- Redis: `EXISTS evento:web:<event_id>` devolvió `1`.
- Redis `GET`: devolvió el JSON del evento, incluyendo `source=web`, `type=click`, `subject_ref=U7`, `product_id=P17` y `recommendation_id=prueba-seguridad-eventos`.
- Logs del consumidor: se encontró el mismo `event_id` en el registro del proceso.
- Dashboard: `eventos_registrados=9`, `redis=true`, `dashboard=operativo` e interacción de producto P17 igual a 9.

Esta comprobación completa la evidencia del evento específico: aceptación HTTP → procesamiento del consumidor → persistencia en Redis → actualización del contador del Dashboard. El resultado describe el entorno EC2 que estaba ejecutándose el 27-11-2026; no significa que la rama de revisión haya sido desplegada.

## Compatibilidad de dependencias y pendientes antes de despliegue

El entorno de entrenamiento registra NumPy 2.3.5, pandas 2.2.3 y joblib 1.5.3. El snapshot de EC2 registra NumPy 2.5.5, pandas 3.1.1 y joblib 1.6.0. Scikit-learn aparece como 1.8.0 en ambos. El artefacto cargó y realizó inferencias en el entorno EC2 observado, pero esta diferencia de versiones debe mantenerse documentada y reproducirse en un entorno controlado.

Antes de desplegar la rama:
- Probar las rutas protegidas de la API con clave correcta, ausente e incorrecta.
- Comparar los archivos desplegados con el commit aprobado.
- Confirmar que el Dashboard siga limitado a loopback o protegido por un mecanismo de acceso.
- Revisar la configuración de secretos fuera de Git.
- Validar el comportamiento con la versión de Python y dependencias que se usarán en el despliegue.

No actualizar producción directamente desde esta rama sin completar estas comprobaciones. La rama `main` no se modifica con esta propuesta.

## Archivos de la rama

- `cloud-source-candidate/security.py`
- `cloud-source-candidate/api.py`
- `cloud-source-candidate/api_respaldo.py`
- `cloud-source-candidate/dashboard_api.py`
- `cloud-source-candidate/env.example`
- `cloud-source-candidate/requirements-runtime-ec2-snapshot.txt`
- `cloud-source-candidate/requirements-test.txt`
- `cloud-source-candidate/tests/test_security.py`
