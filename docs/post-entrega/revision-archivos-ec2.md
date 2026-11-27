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

### `shopfast-dashboard-source.tar.gz` — exportado desde EC2 el 27-11-2026

Incluye:

- `dashboard_api.py`
- `dashboard/index.html`
- `dashboard/app.js`
- `dashboard/styles.css`
- `requirements-ec2-freeze.txt`
- `python-version.txt`
- `systemd/dashboard-service.txt`, salida de `systemctl cat`

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
| Dashboard backend y frontend | Recuperados desde el directorio de trabajo de EC2 |
| Sintaxis de `dashboard_api.py` | Análisis AST correcto |
| Versión Python EC2 | 3.12.3 |
| Snapshot de dependencias EC2 | `pip freeze` de 63 paquetes |
| Dockerfile original de EC2 | No recibido |
| Archivo `.env` | No recibido ni publicado |

El análisis sintáctico no equivale a ejecutar la aplicación ni a probar conexiones AWS/RabbitMQ/Redis. La exportación se copió desde el directorio configurado por systemd; no se comparó el hash de cada archivo con el código cargado en memoria por procesos ya iniciados.

## Hallazgos técnicos

1. La API candidata intenta inferencia SageMaker y, ante excepción, usa el pipeline local. Si ambos modelos fallan, asigna un score contextual simple.
2. El inventario es una estructura en memoria con datos de laboratorio P17/P28 y caducidad de 300 segundos. Se pierde al reiniciar el proceso.
3. La ruta `POST /v1/events` publica a RabbitMQ. El consumidor almacena por clave `evento:{source}:{event_id}` con `SET NX`, y confirma el mensaje después de guardar.
4. El consumidor de recuperación termina intencionalmente antes del ACK para forzar reentrega; es un instrumento de prueba, no el consumidor normal.
5. El productor de prueba se actualizó en la copia publicada para incluir `recommendation_id`, campo requerido por el esquema de evento de la API.
6. La API candidata recibida no muestra autenticación API Key para sus rutas de entrada. El Dashboard, por su parte, exige `SHOPFAST_API_KEY` para invocar el endpoint interno de recomendaciones y la transmite en una cabecera servidor-a-servidor. La ruta `/api/dashboard` no incorpora autenticación propia en este módulo.
7. El servicio systemd del dashboard arranca `dashboard_api:app`. El backend y los recursos estáticos ya fueron recuperados.
8. El RAR no declaraba todos los paquetes importados por la aplicación cloud. El `pip freeze` posterior de EC2 recuperó las versiones instaladas del entorno completo, pero no es una lista mínima de dependencias ni una receta de instalación aislada.
9. El Compose recibido contenía un secreto de prueba incrustado. La copia pública lo reemplaza por variables de entorno obligatorias. Si el secreto original se utilizó en el entorno activo, debe rotarse.
10. No se encontró Dockerfile original en los paquetes recibidos. El Compose incluido solo define RabbitMQ y Redis; no es el despliegue completo de la API.
11. El Dashboard llama al endpoint interno con parámetros fijos de demostración (`U7`, contexto `audio`, límite 5, superficie `home`). Para una integración real debe recibir contexto validado y autorizado, no asumir un usuario fijo.
12. El endpoint de indicadores recorre las claves Redis que coinciden con `evento:*` y construye agregados en memoria en cada petición. Es suficiente para el volumen de laboratorio observado, pero requiere revisión si crece el número de eventos.

## Decisiones de publicación

Se creó `cloud-source-candidate/` para conservar los fuentes revisados sin confundirlos con `prototype-local/`.

Se excluyeron:
- credenciales y valores secretos;
- `.pyc` / `__pycache__`;
- `redis-dump.rdb` por contener eventos runtime;
- `modelo.joblib`, `model.tar.gz` y `ShopFast_datos.zip`, ya ignorados por el repositorio como artefactos binarios/datos;
- el archivo `.env` y cualquier clave PEM.

## Pendientes para declarar el despliegue reproducible

- Recuperar Dockerfile y configuración completa de despliegue, si existen.
- Confirmar autenticación de todas las rutas accesibles y el límite de confianza del túnel SSH.
- Definir un requirements mínimo reproducible separado del `pip freeze` histórico.
- Comparar hashes de los archivos publicados con los de EC2 en una nueva exportación controlada.
- Ejecutar pruebas integradas autorizadas de API, SageMaker, RabbitMQ, Redis y Dashboard.
- Verificar el manejo de errores del frontend ante respuestas incompletas del motor.
