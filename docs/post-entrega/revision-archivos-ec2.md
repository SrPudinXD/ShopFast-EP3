# Auditoría de los archivos ShopFast recibidos

## Archivos inspeccionados

### `shopfast(1).rar`

Incluye:

- `api.py`, `api_respaldo.py`
- `sagemaker_cliente.py`
- `mensajeria.py`
- `consumidor.py`, `consumidor_recuperacion.py`
- `productor.py`, `productor_recuperacion.py`
- `probar.py`, `probar_aws.py`, `pruebas_locales.json`
- `code/inference.py`, `code/requirements.txt`
- `requirements.txt`, `docker-compose.yml`, `LEEME.txt`, `evidencia_terminal.txt`
- `modelo.joblib`, `model.tar.gz`, `ShopFast_datos.zip`
- bytecode `.pyc` y directorios auxiliares

### `shopfast-configuracion.tar.gz`

Incluye tres unidades systemd:

- `shopfast-api.service`
- `shopfast-consumidor.service`
- `shopfast-dashboard.service`

También contiene `redis-dump.rdb`, que es estado runtime y no fuente de aplicación.

## Resultados de revisión

| Comprobación | Resultado |
|---|---|
| Sintaxis de los 11 archivos Python del RAR | Todos se pudieron analizar sintácticamente |
| Manifiesto SHA-256 de los nueve CSV del ZIP de datos | Todos coinciden |
| Modelo dentro de `model.tar.gz` vs `modelo.joblib` raíz | Coinciden |
| Código de API que llama a SageMaker | Presente en `api.py` |
| Respaldo Random Forest local | Presente |
| Publicación RabbitMQ y confirmación durable | Presente en `mensajeria.py` |
| Deduplicación Redis antes del ACK | Presente en `consumidor.py` |
| Prueba de interrupción antes del ACK | Presente en consumidor de recuperación |
| Fuente del dashboard | Ausente |
| Dockerfile original de EC2 | Ausente |
| Archivo `.env` / versiones completas de entorno | Ausentes |

El análisis sintáctico no equivale a ejecutar la aplicación ni a probar conexiones AWS/RabbitMQ/Redis.

## Hallazgos técnicos

1. La API candidata intenta inferencia SageMaker y, ante excepción, usa el pipeline local. Si ambos modelos fallan, asigna un score contextual simple.
2. El inventario es una estructura en memoria con datos de laboratorio P17/P28 y caducidad de 300 segundos. Se pierde al reiniciar el proceso.
3. La ruta `POST /v1/events` publica a RabbitMQ. El consumidor almacena por clave `evento:{source}:{event_id}` con `SET NX`, y confirma el mensaje después de guardar.
4. El consumidor de recuperación termina intencionalmente antes del ACK para forzar reentrega; es un instrumento de prueba, no el consumidor normal.
5. El productor de prueba se actualizó en la copia publicada para incluir `recommendation_id`, campo requerido por el esquema de evento de la API.
6. El código recibido no muestra autenticación API Key. La documentación del sistema menciona esa protección, pero no se encontró en el módulo API exportado.
7. El servicio systemd del dashboard arranca `dashboard_api:app`, pero el archivo no está en el RAR.
8. El requirements exportado no declara los paquetes `boto3`, `pika` y `redis`, aunque el código los importa. Se agregó una lista cloud candidata; faltan las versiones exactas instaladas en EC2.
9. El Compose recibido contiene un secreto de prueba incrustado. La copia pública lo reemplaza por variables de entorno obligatorias. Si el secreto original se utilizó en el entorno activo, debe rotarse.
10. No se encontró Dockerfile en los paquetes recibidos. El Compose incluido solo define RabbitMQ y Redis; no es el despliegue completo de la API.

## Decisiones de publicación

Se creó `cloud-source-candidate/` para conservar los fuentes revisados sin confundirlos con `prototype-local/`.

Se excluyeron:
- credenciales y valores secretos;
- `.pyc` / `__pycache__`;
- `redis-dump.rdb` por contener eventos runtime;
- `modelo.joblib`, `model.tar.gz` y `ShopFast_datos.zip`, ya ignorados por el repositorio como artefactos binarios/datos.

El paquete de datos se verificó internamente, pero su publicación no es necesaria para incorporar la fuente Python. El artefacto de modelo puede recuperarse/reproducirse siguiendo las instrucciones de entrenamiento y los controles de integridad ya documentados.

## Pendientes para declarar el despliegue reproducible

- Obtener dashboard backend y frontend.
- Confirmar autenticación en API, proxy o capa externa.
- Obtener `pip freeze` del entorno virtual EC2.
- Comparar hashes de los archivos publicados con los de EC2.
- Recuperar el Dockerfile y configuración de despliegue de la aplicación, si existen.
- Ejecutar pruebas integradas autorizadas en un entorno controlado.
