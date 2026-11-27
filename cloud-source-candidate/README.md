# ShopFast — código cloud recuperado desde EC2

Esta carpeta reúne snapshots sanitizados de los fuentes entregados en `shopfast(1).rar`, de `shopfast-configuracion.tar.gz` y del paquete `shopfast-dashboard-source.tar.gz` exportado desde EC2 el 27-11-2026.

**Alcance:** código recuperado desde los archivos y directorios configurados en EC2. No se ha realizado una comparación byte a byte contra todos los procesos cargados en memoria ni una reconstrucción completa desde cero. Esta carpeta no reemplaza el prototipo local de `prototype-local/`.

## Estructura

- Raíz: API cloud, cliente SageMaker, mensajería RabbitMQ, productores y consumidores.
- `code/`: handler de inferencia SageMaker y dependencias de ese handler.
- `dashboard_api.py`: backend FastAPI del Dashboard.
- `dashboard/`: frontend HTML, CSS, JavaScript y notas específicas del panel.
- `systemd/`: unidades de API, consumidor y Dashboard, más el override de entorno del Dashboard.
- `tests/`: scripts y resultados de pruebas recibidos.
- `docker-compose.yml`: RabbitMQ y Redis con puertos ligados a loopback.

## Dependencias y entorno EC2

- `requirements-exported.txt`: archivo de dependencias incluido en el RAR original.
- `requirements-ec2-freeze-2026-11-27.txt`: snapshot de `pip freeze` del entorno virtual completo de EC2; no es un requirements mínimo.
- `python-version-ec2.txt`: versión Python reportada por EC2 (3.12.3).

No instalar automáticamente el snapshot completo en producción sin revisar compatibilidad, dependencias transitivas y necesidad real de cada paquete.

## Dashboard recuperado

La unidad systemd ejecuta `dashboard_api:app` con Uvicorn en `127.0.0.1:8080`. El backend consulta Redis en `127.0.0.1:6379` y llama al motor de recomendaciones local en `127.0.0.1:8000`. La variable `SHOPFAST_API_KEY` se obtiene desde el entorno del proceso y se envía al motor interno en la cabecera `X-API-Key`; no se expone al navegador.

La consulta de recomendaciones usa parámetros fijos de demostración (`subject_ref=U7`, `context=audio`, `limit=5`, `surface=home`). La ruta `/api/dashboard` no incorpora autenticación propia en este módulo. Mantener el panel en loopback y acceder por túnel SSH, o añadir una capa de autenticación antes de exponerlo.

## Sanitización

Se retiraron las contraseñas de prueba incrustadas en scripts y Compose del paquete RAR original. No se publicaron `.env`, credenciales AWS, claves privadas, archivos `.pyc`, el volcado Redis ni binarios de modelo/datos.

## Limitaciones conocidas

- El inventario de la API candidata es simulado y se mantiene en memoria; no es integración comercial ni reserva stock.
- El Dashboard usa un usuario/contexto fijo de demostración.
- La API cloud recibida no muestra autenticación API Key propia para sus rutas de entrada.
- El escaneo de Redis recorre las claves `evento:*` para calcular los indicadores; conviene mantener agregados o paginar si aumenta el volumen.
- No se recibió el Dockerfile original de EC2.
- No se han repetido pruebas integradas desde cero ni comparado cada hash con el estado de procesos activos.



## Reviewed hardening branch

The branch `review/cloud-hardening` contains proposed corrections while the `main` branch preserves the sanitized source snapshot:

- API key validation for recommendation and event routes, using constant-time comparison.
- Four isolated unit tests for missing server configuration, missing/wrong client key, and valid key.
- Removal of a duplicate Dashboard route decorator and handling of invalid JSON responses.
- A direct runtime requirements file based on the versions observed in the EC2 `pip freeze`.

To run the isolated tests from this directory:

```bash
python -m pip install -r requirements-test.txt
python -m pytest tests/test_security.py
```

The API key must be configured as `SHOPFAST_API_KEY` in the server's untracked `.env` file. Do not commit that file. Keep the Dashboard and API bound to loopback and use the SSH tunnel. The Dashboard indicators endpoint still has no application-level authentication of its own.

**Before deployment:** the recorded model-training dependencies and the EC2 runtime snapshot differ for NumPy, pandas and joblib. Re-load the exact model artifact and run an authorized SageMaker/API smoke test in a staging copy before applying these changes to EC2. The full integration suite was not run because model and dataset binaries are intentionally not stored in Git.

Ver [auditoría de los archivos EC2](../docs/post-entrega/revision-archivos-ec2.md) y [brechas cloud pendientes](../docs/cloud-source-gap.md).
