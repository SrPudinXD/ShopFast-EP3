# Arquitectura ShopFast

Cliente web/móvil → API REST → verificación de inventario conocido/vigente → inferencia SageMaker → ranking → respuesta. Si falla la inferencia cloud, se documenta Random Forest local como ruta alternativa.

Eventos REST → RabbitMQ → consumidor → deduplicación por fuente + ID → Redis → dashboard.

Despliegue documentado: EC2 Ubuntu en Ohio, API y dashboard en loopback, consumidor systemd, RabbitMQ/Redis en Docker, invocación SageMaker por Boto3/IAM, artefacto en S3 y observabilidad CloudWatch. No existe alta disponibilidad multizona.

Límites: inventario simulado de 300 s; no hay integración comercial ni reserva de stock. Checkout debe seguir operando ante fallo del recomendador. La caché de candidatos es propuesta futura, no implementada.

**Fuente:** el código cloud completo no estaba en el paquete recuperado. prototype-local contiene únicamente la API de prototipo local.