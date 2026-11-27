# Estado del código cloud recibido y brechas pendientes

## Material recibido

Se revisaron los dos archivos compartidos para completar la fuente ShopFast:

- `shopfast(1).rar`: contiene API, cliente SageMaker, mensajería RabbitMQ, consumidor Redis, productores de prueba, handler de inferencia, dependencias, pruebas y artefactos del modelo/datos.
- `shopfast-configuracion.tar.gz`: contiene las unidades systemd de API, consumidor y dashboard, además de un volcado Redis.

Se publicó una copia de código sanitizada y separada del prototipo local en [cloud-source-candidate/](../cloud-source-candidate/). No se reemplazó `prototype-local/`.

## Qué se incorporó

- `api.py`: intenta inferencia SageMaker y usa Random Forest local como respaldo.
- `sagemaker_cliente.py`: cliente Boto3 para el endpoint.
- `mensajeria.py`: publicación durable en RabbitMQ.
- `consumidor.py`: deduplicación por fuente + ID y escritura Redis antes del ACK.
- Productores y consumidor de recuperación para pruebas.
- Handler de inferencia SageMaker y sus dependencias.
- Compose sanitizado y unidades systemd.
- Scripts y resultados de pruebas locales.
- Plantilla de variables de entorno sin credenciales.

La configuración de SageMaker y RabbitMQ se hizo configurable por variables de entorno en la copia publicada. Las contraseñas incrustadas en scripts/Compose fueron retiradas. Si alguna credencial del archivo original se utilizó en EC2, debe rotarse.

## Diferencias verificadas y brechas

1. **Dashboard ausente:** la unidad `shopfast-dashboard.service` ejecuta `dashboard_api:app`, pero el RAR no incluye `dashboard_api.py` ni archivos dentro de `dashboard/`. La implementación del dashboard sigue sin estar disponible.
2. **Autenticación API Key no demostrada en el código recibido:** el `api.py` entregado no contiene middleware, dependencia ni validación de API Key. La documentación arquitectónica previa mencionaba esa protección; no se debe afirmar que esta copia la implementa.
3. **Dependencias incompletas:** el `requirements.txt` original no declara `boto3`, `pika` ni `redis`, aunque los módulos cloud los importan. Se añadió `requirements-cloud.txt` como lista candidata, no como lockfile real de EC2.
4. **Configuración no entregada:** las unidades API/consumidor hacen referencia a `/home/ubuntu/shopfast/.env`, pero ese archivo no fue incluido y no se publica.
5. **Inventario simulado:** el código mantiene stock en memoria, inicializa P17/P28 con cantidades de laboratorio y aplica vencimiento de 300 segundos. No integra inventario comercial ni reserva unidades.
6. **Proveniencia:** los archivos se recibieron como exportación para revisión, pero no hay hash de commit/despliegue ni comparación directa contra procesos activos de EC2. Se etiquetan como código cloud candidato, no como prueba de ejecución actual.
7. **Pruebas:** `pruebas_locales.json` contiene diez resultados OK aportados por el paquete. No se ejecutaron de nuevo en este entorno ni demuestran disponibilidad AWS actual.

## Archivos excluidos deliberadamente

- `.env`, contraseñas y secretos.
- Archivos `.pyc` y `__pycache__/`.
- `redis-dump.rdb`, porque es estado runtime con eventos de prueba, no fuente reproducible.
- `modelo.joblib`, `model.tar.gz` y `ShopFast_datos.zip`, porque el repositorio los excluye por `.gitignore` y son artefactos binarios/datos. El ZIP de datos sí pasó sus nueve verificaciones SHA-256 internas; el modelo dentro de `model.tar.gz` coincide con `modelo.joblib` del mismo archivo.

## Próximos pasos para cerrar la brecha

- Recuperar `dashboard_api.py`, `dashboard/index.html`, CSS y JavaScript.
- Obtener el `.env` solo en EC2 para inventariar nombres de variables, sin copiar sus valores a GitHub.
- Obtener `pip freeze` del entorno virtual EC2 y fijar dependencias exactas.
- Confirmar si la API Key se aplica en un proxy, middleware externo o en otro archivo no entregado.
- Comparar hashes de los fuentes con los archivos del servidor y registrar el commit/despliegue.
- Ejecutar pruebas integradas autorizadas y documentar sus resultados reales.

No etiquetar el Dockerfile raíz como Dockerfile de EC2: ese archivo sigue construyendo únicamente el prototipo local.
