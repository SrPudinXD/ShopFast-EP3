# Índice de evidencias

El paquete de preentrega contiene 305 capturas sanitizadas: 275 originales y 30 adicionales del 27/11. Se excluyó una captura que mostraba una API Key.

- E42: despliegue/modelo cloud e infraestructura.
- E47: inferencia cloud y filtro de inventario.
- E49: persistencia de evento y ACK.
- E52–53: reentrega e idempotencia.
- E54–56: fallback y recuperación de inferencia cloud.
- E57: health check.
- E61–62: reinicio EC2/servicios y persistencia.
- E63–67: seguridad, API Key, eventos y controles de inventario.
- E69–71: dashboard y eventos de prueba.
- E72–80: rendimiento, operación, métricas y CloudWatch.
- E81–83: costos y Cost Explorer.
- E84–92: respaldos.
- E93: reinicio de API y respuesta inicial.
- E94: inferencia SageMaker HTTP 200, rf-cloud-v1, fallback=false.
- E95: instalación de Locust.
- E96: resumen de prueba Locust.
- E97: CSV exportado.

Una captura demuestra el estado mostrado en ese momento, no disponibilidad continua. Eventos e inventario son de laboratorio/simulados. E93–E97 corresponden a la prueba de 10 usuarios. El ZIP de capturas se conserva en el paquete AVA; las imágenes no se subieron en este commit.
