# Arquitectura ShopFast

Cliente web/móvil → API REST FastAPI → validación API Key → filtro de inventario conocido/vigente → SageMaker → ranking → respuesta JSON. Si falla la inferencia cloud, el informe documenta Random Forest local como alternativa.

Los eventos se reciben por REST, se publican en RabbitMQ, los procesa un consumidor, se deduplican por fuente + ID, se persisten en Redis y se confirman con ACK. El dashboard consulta Redis.

Despliegue documentado: EC2 Ubuntu en Ohio, API y dashboard en loopback, consumidor systemd, RabbitMQ/Redis en Docker, SageMaker mediante Boto3/IAM, S3 para el artefacto y CloudWatch para observabilidad. No hay alta disponibilidad multizona.

Límites: inventario simulado con vencimiento de 300 s, sin integración comercial ni reserva de stock. El checkout debe continuar si falla el recomendador. La caché de candidatos es propuesta futura, no implementación.

El código de prototype-local/ es la fuente local recibida. El código exacto desplegado en EC2 no estaba incluido en el paquete fuente recuperado; ver cloud-source-gap.md.
