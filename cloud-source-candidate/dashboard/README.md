# Dashboard ShopFast — exportación de EC2

Estos archivos se recuperaron del paquete `shopfast-dashboard-source.tar.gz`, generado en la instancia EC2 y descargado el 27-11-2026.

## Archivos

- `dashboard_api.py`: backend FastAPI del panel.
- `dashboard/index.html`: estructura de la interfaz.
- `dashboard/app.js`: consulta los indicadores cada 10 segundos y permite consultar recomendaciones.
- `dashboard/styles.css`: estilos responsive del panel.

## Configuración observada en la instancia

- Python: 3.12.3.
- Servicio systemd: `shopfast-dashboard.service`.
- Uvicorn: `dashboard_api:app --host 127.0.0.1 --port 8080`.
- Redis: `127.0.0.1:6379`.
- Motor de recomendaciones: `http://127.0.0.1:8000/v1/recommendations`.
- Variable de entorno requerida por la consulta de recomendaciones: `SHOPFAST_API_KEY`.

El servicio se ejecutaba en loopback, no enlazado directamente a una interfaz pública. El archivo de configuración systemd exportado se conserva en `../systemd/dashboard-service-export.txt`.

## Comportamiento observado en el código

1. `GET /api/dashboard` consulta claves Redis que coinciden con `evento:*`, calcula conteos por tipo y producto y devuelve el estado del Redis.
2. `GET /api/recomendaciones` obtiene `SHOPFAST_API_KEY` desde el entorno del proceso y la envía como cabecera `X-API-Key` al servicio local de recomendaciones.
3. La solicitud de recomendaciones está fijada en el código a `subject_ref=U7`, `context=audio`, `limit=5` y `surface=home`.
4. La interfaz consulta los indicadores cada 10 segundos y presenta resultados del motor cuando se pulsa el botón correspondiente.

## Limitaciones y observaciones para una mejora posterior

- La ruta `/api/dashboard` no incorpora autenticación propia en este módulo. La unidad systemd la enlaza a loopback; conservar el acceso por túnel SSH o añadir una capa de autenticación antes de exponer el panel.
- La ruta `/api/recomendaciones` usa la clave para autenticarse ante el motor interno; la clave no se entrega al navegador.
- La consulta de recomendaciones usa un usuario/contexto fijo de demostración, no datos dinámicos del usuario conectado.
- El escaneo Redis recorre todas las claves `evento:*` y materializa el conjunto en memoria; conviene paginar o mantener agregados si crece el volumen.
- El export de dependencias es un `pip freeze` del entorno completo de EC2, no un requirements mínimo exclusivo del Dashboard.
- No se modificó el código fuente recuperado. Las mejoras anteriores son recomendaciones, no cambios ya desplegados.

## Seguridad

No contiene el archivo `.env`, API Keys, credenciales AWS, PEM ni el volcado Redis. No copiar secretos al repositorio. No utilizar este snapshot como despliegue nuevo sin revisar las dependencias y configuración del entorno.
