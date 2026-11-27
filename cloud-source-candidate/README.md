# ShopFast — código cloud recuperado desde EC2

Esta carpeta reúne snapshots sanitizados de los fuentes entregados en `shopfast(1).rar`, `shopfast-configuracion.tar.gz` y `shopfast-dashboard-source.tar.gz`, exportado desde EC2 el 27-11-2026.

**Alcance:** son copias de los archivos recibidos y configurados en EC2. No se compararon byte a byte con todos los procesos activos ni se reconstruyó el despliegue completo desde cero. Esta carpeta no reemplaza el prototipo local de `prototype-local/`.

## Estructura

- Raíz: API cloud, cliente SageMaker, mensajería RabbitMQ, productores y consumidores.
- `code/`: handler de inferencia SageMaker y dependencias del handler.
- `dashboard_api.py` y `dashboard/`: backend y frontend del Dashboard.
- `systemd/`: unidades de API, consumidor y Dashboard, más el override de entorno.
- `tests/`: pruebas recibidas y pruebas unitarias de seguridad propuestas.
- `docker-compose.yml`: RabbitMQ y Redis, con puertos ligados a loopback.

## Dependencias y entorno EC2

- `requirements-exported.txt`: dependencias incluidas en el RAR original.
- `requirements-ec2-freeze-2026-11-27.txt`: snapshot completo de `pip freeze` del entorno virtual de EC2.
- `requirements-runtime-ec2-snapshot.txt`: dependencias runtime directas, fijadas a versiones observadas en ese snapshot.
- `requirements-test.txt`: FastAPI, HTTPX y pytest para ejecutar las pruebas unitarias y de dependencia aisladas.
- `python-version-ec2.txt`: Python 3.12.3, según la exportación recibida.

El snapshot completo no es un archivo mínimo de instalación. No instalarlo automáticamente en producción sin revisar compatibilidad y necesidad de cada paquete.

## Dashboard recuperado

La unidad systemd ejecuta `dashboard_api:app` con Uvicorn en `127.0.0.1:8080`. El backend consulta Redis en `127.0.0.1:6379` y llama al motor de recomendaciones en `127.0.0.1:8000`. La variable `SHOPFAST_API_KEY` se obtiene desde el entorno del proceso y se envía al motor interno mediante `X-API-Key`; no se expone al navegador.

La consulta de recomendaciones utiliza parámetros fijos de demostración (`subject_ref=U7`, `context=audio`, `limit=5`, `surface=home`). La ruta `/api/dashboard` no tiene autenticación propia en este módulo. Mantener el panel en loopback y acceder mediante túnel SSH; no exponerlo directamente.

## Sanitización

No se publicaron `.env`, credenciales AWS, claves privadas, archivos `.pyc`, volcados Redis ni binarios del modelo/dataset. Las contraseñas de prueba incrustadas en el paquete RAR original se sustituyeron por marcadores o se retiraron.

## Limitaciones conocidas del snapshot original

- El inventario de la API es simulado y se mantiene en memoria; no es integración comercial ni reserva stock.
- El Dashboard utiliza un usuario/contexto fijo de demostración.
- La API del snapshot original no validaba su propia cabecera API Key en las rutas de entrada.
- El escaneo Redis recorre las claves `evento:*` para calcular indicadores; conviene mantener agregados o paginar si aumenta el volumen.
- No se recibió el Dockerfile original de EC2.
- No se repitieron pruebas integradas ni se compararon todos los hashes con los archivos activos de EC2.

## Rama de revisión técnica: `review/cloud-hardening`

La rama contiene cambios propuestos; `main` conserva el snapshot previo:

- `security.py` valida `X-API-Key` mediante comparación en tiempo constante.
- `GET /v1/recommendations` y `POST /v1/events` requieren `SHOPFAST_API_KEY`.
- `GET /health/live` se mantiene público para comprobaciones de vida.
- Se eliminó el decorador duplicado de `/api/recomendaciones` y se controla JSON inválido del motor interno.
- Se añadieron seis pruebas unitarias/de dependencia para el validador y la dependencia FastAPI.
- Se agregó un archivo de dependencias runtime basado en versiones observadas en EC2.

Para ejecutar las pruebas desde esta carpeta:

```bash
python -m pip install -r requirements-test.txt
python -m pytest tests/test_security.py
```

El servidor debe tener `SHOPFAST_API_KEY` en su archivo `.env` local no versionado. Nunca subir ese archivo ni la clave real.

**Validación runtime EC2 (27-11-2026):** se comprobó que el modelo y el ZIP del dataset cargan en la instancia; la inferencia local y SageMaker se ejecutaron correctamente con resultados coincidentes para tres entradas. API y Dashboard respondieron HTTP 200. Redis respondió PONG; RabbitMQ y el consumidor procesaron un evento nuevo, que quedó visible en Redis y elevó el contador del Dashboard de 7 a 8. Estos resultados corresponden al entorno EC2 existente, no al despliegue de esta rama.

**Antes de desplegar esta rama:** probar las rutas protegidas con claves correctas e incorrectas, revisar los archivos y secretos efectivos, y confirmar que el Dashboard siga limitado a loopback o protegido por un mecanismo de acceso. El entorno de entrenamiento y EC2 difieren en NumPy, pandas y joblib; conservar esa diferencia documentada y validarla en un entorno controlado.

Ver [auditoría de archivos EC2](../docs/post-entrega/revision-archivos-ec2.md), [brechas cloud pendientes](../docs/cloud-source-gap.md) y [revisión técnica](../docs/security-review.md).
