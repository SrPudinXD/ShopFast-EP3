# Dashboard ShopFast — snapshot recuperado de EC2

Estos archivos se recuperaron del paquete `shopfast-dashboard-source.tar.gz`, exportado desde la instancia EC2 el 27-11-2026.

## Archivos

- `../dashboard_api.py`: backend FastAPI.
- `index.html`: estructura de la interfaz.
- `app.js`: consulta indicadores cada 10 segundos y permite consultar recomendaciones.
- `styles.css`: estilos responsive.

## Configuración observada

- Python: 3.12.3.
- Servicio: `shopfast-dashboard.service`.
- Uvicorn: `dashboard_api:app --host 127.0.0.1 --port 8080`.
- Redis: `127.0.0.1:6379`.
- Motor de recomendaciones: `http://127.0.0.1:8000/v1/recommendations`.
- Variable requerida para la consulta de recomendaciones: `SHOPFAST_API_KEY`.

La unidad está en [systemd/shopfast-dashboard.service](../systemd/shopfast-dashboard.service) y el override `EnvironmentFile` en [systemd/shopfast-dashboard.service.d/environment.conf](../systemd/shopfast-dashboard.service.d/environment.conf).

## Comportamiento observado

1. `GET /api/dashboard` consulta claves Redis `evento:*`, calcula conteos por tipo y producto y devuelve el estado de Redis.
2. `GET /api/recomendaciones` obtiene `SHOPFAST_API_KEY` desde el entorno del proceso y la envía como cabecera `X-API-Key` al servicio local de recomendaciones.
3. La solicitud de recomendaciones está fijada en `subject_ref=U7`, `context=audio`, `limit=5` y `surface=home`.
4. La interfaz consulta indicadores cada 10 segundos y muestra resultados del motor al pulsar el botón.

## Limitaciones y seguridad

- `/api/dashboard` no incorpora autenticación propia en este módulo. La unidad systemd la enlaza a loopback; conservar el acceso por túnel SSH o añadir una capa de autenticación antes de exponer el panel.
- La clave no se entrega al navegador; se usa desde el backend para invocar el motor interno.
- La consulta utiliza un usuario/contexto fijo de demostración, no datos dinámicos del usuario conectado.
- El escaneo Redis recorre todas las claves `evento:*`; conviene paginar o mantener agregados si crece el volumen.
- El snapshot `pip freeze` corresponde al entorno virtual completo de EC2, no a dependencias mínimas del Dashboard.

Este directorio conserva el snapshot recuperado; las mejoras descritas son recomendaciones y no cambios desplegados en EC2.
