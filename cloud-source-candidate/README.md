# ShopFast — código cloud candidato (exportaciones recibidas desde EC2)

Esta carpeta reúne una copia revisada y sanitizada de los fuentes entregados en `shopfast(1).rar`, de `shopfast-configuracion.tar.gz` y del paquete `shopfast-dashboard-source.tar.gz` exportado desde EC2 el 27-11-2026.

**Importante:** son snapshots de archivos recuperados desde el entorno EC2. No se ha realizado una comparación byte a byte contra todos los procesos que estaban cargados en memoria ni una reconstrucción completa desde cero. No se reemplaza el prototipo local de `prototype-local/`.

## Contenido publicado

- `api.py`: API candidata que intenta inferencia SageMaker y utiliza el modelo local como respaldo.
- `api_respaldo.py`: variante de respaldo con inferencia local.
- `sagemaker_cliente.py`: invocación del endpoint SageMaker.
- `mensajeria.py`: publicación durable en RabbitMQ.
- `consumidor.py`: deduplicación por origen e ID y persistencia Redis antes del ACK.
- `consumidor_recuperacion.py`: consumidor de prueba que termina intencionalmente antes del ACK para probar reentrega/idempotencia. **No usar como servicio normal.**
- `productor.py` y `productor_recuperacion.py`: productores de eventos de laboratorio.
- `docker-compose.yml`: RabbitMQ y Redis con puertos ligados a loopback.
- `code/`: handler y dependencias de inferencia SageMaker.
- `systemd/`: unidades de servicio recibidas.
- `dashboard_api.py` y `dashboard/`: backend FastAPI y frontend HTML/CSS/JS del Dashboard recuperados desde EC2.
- `systemd/dashboard-service-export.txt`: salida de `systemctl cat`, incluye la unidad y su override EnvironmentFile.
- `requirements-ec2-freeze-2026-11-27.txt`: snapshot de `pip freeze` del entorno virtual EC2 completo, no requirements mínimos del Dashboard.
- `python-version-ec2.txt`: versión Python reportada por EC2.
- `requirements-exported.txt`: dependencias originales tal como aparecieron en el RAR.
- `requirements-cloud.txt`: añade dependencias que los imports cloud requieren.
- `env.example`: nombres de variables requeridas, sin secretos.

## Sanitización aplicada

Se retiraron las contraseñas de prueba incrustadas en scripts y Compose del paquete RAR original. La versión publicada obtiene credenciales RabbitMQ desde variables de entorno. No se publicaron `.env`, credenciales AWS, claves privadas, archivos `.pyc`, el volcado Redis ni datos runtime. El export del Dashboard no contenía valores de claves API ni credenciales.

Los binarios `modelo.joblib`, `model.tar.gz` y `ShopFast_datos.zip` se mantienen fuera de esta carpeta: el repositorio los excluye intencionalmente mediante `.gitignore`.

## Dashboard recuperado

La unidad systemd exportada ejecuta `dashboard_api:app` con Uvicorn en `127.0.0.1:8080`. El backend consulta Redis en `127.0.0.1:6379` y llama al motor de recomendaciones local en `127.0.0.1:8000`. La consulta usa `SHOPFAST_API_KEY` desde el entorno del proceso y no expone esa clave al navegador.

La ruta `/api/dashboard` no incorpora autenticación propia en este módulo; el servicio se encontraba enlazado a loopback. Mantener acceso por túnel SSH o incorporar una capa de autenticación antes de exponer el panel.

## Verificaciones y pendientes

1. El backend del Dashboard y sus tres recursos estáticos ya fueron recuperados desde el directorio de trabajo configurado en la unidad systemd.
2. La sintaxis Python de `dashboard_api.py` fue analizada correctamente. Esto no sustituye una prueba de integración en ejecución.
3. El snapshot `pip freeze` contiene 63 paquetes del entorno virtual completo. No es un archivo mínimo ni debe instalarse indiscriminadamente en un entorno nuevo.
4. El endpoint de recomendaciones del Dashboard utiliza una consulta fija de demostración: `subject_ref=U7`, `context=audio`, `limit=5` y `surface=home`.
5. El servicio depende de `/home/ubuntu/shopfast/.env`; ese archivo de entorno no fue entregado y no se publica.
6. La API candidata mantiene inventario simulado en memoria; no es una integración comercial ni reserva stock.
7. No se ha probado el despliegue desde cero con todos estos archivos ni se ha verificado el funcionamiento integrado de los servicios tras una reinstalación.

Antes de usarlo como despliegue reproducible, definir dependencias mínimas, comprobar autenticación de todas las rutas, recuperar el Dockerfile/configuración de despliegue originales si existen y ejecutar pruebas controladas.
