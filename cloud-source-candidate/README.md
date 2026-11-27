# ShopFast — código cloud candidato (exportación recibida)

Esta carpeta contiene una copia revisada y sanitizada de los fuentes entregados en `shopfast(1).rar` y de las unidades systemd de `shopfast-configuracion.tar.gz`.

**Importante:** es una exportación candidata asociada al entorno EC2, no una verificación independiente de que cada archivo coincida byte a byte con el proceso actualmente activo. No se reemplaza el prototipo local de `prototype-local/`.

## Contenido publicado

- `api.py`: API que intenta inferencia SageMaker y utiliza el modelo local como respaldo.
- `api_respaldo.py`: variante de respaldo con inferencia local.
- `sagemaker_cliente.py`: invocación del endpoint SageMaker.
- `mensajeria.py`: publicación durable en RabbitMQ.
- `consumidor.py`: deduplicación por origen e ID y persistencia Redis antes del ACK.
- `consumidor_recuperacion.py`: consumidor de prueba que termina intencionalmente antes del ACK para probar reentrega/idempotencia. **No usar como servicio normal.**
- `productor.py` y `productor_recuperacion.py`: productores de eventos de laboratorio.
- `docker-compose.yml`: RabbitMQ y Redis con puertos ligados a loopback.
- `code/`: handler y dependencias de inferencia SageMaker.
- `systemd/`: unidades de servicio recibidas.
- `requirements-exported.txt`: dependencias originales tal como aparecieron en el RAR.
- `requirements-cloud.txt`: añade dependencias que los imports cloud requieren.
- `env.example`: nombres de variables requeridas, sin secretos.

## Sanitización aplicada

Se retiraron las contraseñas de prueba incrustadas en scripts y Compose. La versión publicada obtiene credenciales RabbitMQ desde variables de entorno. No se publicaron `.env`, credenciales AWS, claves privadas, archivos `.pyc`, el volcado Redis ni datos runtime.

Los binarios `modelo.joblib`, `model.tar.gz` y `ShopFast_datos.zip` se mantienen fuera de esta carpeta: el repositorio los excluye intencionalmente mediante `.gitignore`. El archivo de datos del RAR sí pasó la verificación de sus nueve hashes SHA-256 internos. El modelo incluido en `model.tar.gz` coincide con `modelo.joblib` del mismo RAR.

## Verificaciones y pendientes

1. El servicio `shopfast-dashboard.service` apunta a `dashboard_api:app`, pero el RAR no contiene `dashboard_api.py` ni archivos dentro de `dashboard/`. El código del dashboard sigue pendiente.
2. La API recibida no implementa validación de API Key, aunque la documentación arquitectónica describe esa protección. No afirmar que esta copia aplica API Key.
3. `requirements-exported.txt` no declara `boto3`, `pika` ni `redis`, que sí se importan en el código cloud. `requirements-cloud.txt` agrega esos paquetes, pero no es un lockfile reproducido desde EC2.
4. Los servicios systemd dependen de `/home/ubuntu/shopfast/.env` y de un entorno virtual existente en EC2. Ese archivo de entorno no fue entregado y no se publica.
5. La API mantiene inventario simulado en memoria; no es una integración comercial ni reserva stock.
6. No se ha probado el despliegue desde cero con estos archivos ni se ha comparado el contenido con el filesystem activo de EC2.

Antes de usarlo como despliegue reproducible, recuperar el dashboard faltante, comprobar las versiones reales de dependencias en EC2, verificar el mecanismo de autenticación y ejecutar pruebas controladas.
