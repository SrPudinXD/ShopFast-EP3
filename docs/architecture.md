# Arquitectura ShopFast

## Flujo de recomendación documentado

Cliente web/móvil → API REST FastAPI → validación de solicitud → filtro de inventario conocido/vigente → SageMaker → ranking → respuesta JSON. Si falla la inferencia cloud, el código recibido incluye Random Forest local como respaldo.

**Importante sobre autenticación:** la documentación previa describe validación API Key, pero el `api.py` recibido en el archivo RAR no implementa esa validación en el propio código. Debe verificarse si existe en un proxy, middleware externo u otro módulo no entregado antes de afirmar que está aplicada.

## Flujo de eventos

Los eventos se reciben por REST, se publican en RabbitMQ, los procesa un consumidor, se deduplican por fuente + ID y se persisten en Redis antes de confirmarse con ACK. El consumidor de recuperación permite simular una interrupción antes del ACK para comprobar reentrega e idempotencia. El dashboard está descrito como consumidor de Redis, pero su módulo fuente no venía en los archivos recibidos.

## Despliegue documentado

EC2 Ubuntu en Ohio, API y dashboard en loopback, consumidor systemd, RabbitMQ/Redis en Docker, SageMaker mediante Boto3/IAM, S3 para el artefacto y CloudWatch para observabilidad. Las unidades systemd recibidas hacen referencia a `/home/ubuntu/shopfast/.env`. El archivo `.env` no se publicó.

La copia sanitizada de la exportación recibida está en [cloud-source-candidate/](../cloud-source-candidate/). No se ha verificado contra procesos activos de EC2 ni se dispone de hash de despliegue.

## Límites

- Inventario simulado en memoria con vencimiento de 300 s; sin integración comercial ni reserva de stock.
- El checkout debe continuar si falla el recomendador.
- No hay alta disponibilidad multizona demostrada.
- El dashboard no puede reconstruirse desde los archivos entregados: falta `dashboard_api.py` y su contenido estático.
- La autenticación API Key no está implementada en el `api.py` recibido y requiere verificación.
- Las dependencias exportadas no fijan las versiones de Boto3, Pika y Redis.
- La caché de candidatos es propuesta futura, no implementación.

El código de `prototype-local/` sigue siendo el prototipo local. La carpeta `cloud-source-candidate/` contiene una copia revisada y sanitizada del código cloud recibido; no sustituye ni se presenta como despliegue verificado.
