# Arquitectura ShopFast

## Flujo de recomendación

Cliente web/móvil → API REST FastAPI → validación de solicitud → filtro de inventario conocido/vigente → SageMaker → ranking → respuesta JSON. El código cloud recibido incluye Random Forest local como alternativa cuando falla la inferencia cloud.

El inventario disponible en el laboratorio es simulado, vive en memoria y tiene una vigencia configurada de 300 segundos. No existe integración comercial ni reserva de stock.

**Autenticación:** el `api.py` recibido no muestra validación API Key en sus rutas de entrada. No afirmar que la API esté protegida hasta verificar si esa función se aplica en un proxy, middleware externo u otro módulo.

## Flujo de eventos

Los eventos se reciben por REST, se publican en RabbitMQ, los procesa un consumidor, se deduplican por fuente + ID y se persisten en Redis antes de confirmarse con ACK. El consumidor de recuperación permite simular una interrupción antes del ACK para comprobar reentrega e idempotencia.

## Dashboard

El Dashboard fue recuperado desde la exportación de EC2 del 27-11-2026:

- Backend: `cloud-source-candidate/dashboard_api.py`.
- Interfaz: `cloud-source-candidate/dashboard/index.html`.
- Lógica del navegador: `cloud-source-candidate/dashboard/app.js`.
- Estilos: `cloud-source-candidate/dashboard/styles.css`.

El backend consulta Redis para construir indicadores y llama al motor local de recomendaciones mediante `SHOPFAST_API_KEY`. La solicitud de recomendaciones usa parámetros fijos de demostración (`subject_ref=U7`, contexto `audio`, límite 5 y superficie `home`). La ruta `/api/dashboard` no incorpora autenticación propia en este módulo.

## Despliegue documentado

EC2 Ubuntu en Ohio, API y Dashboard en loopback, consumidor systemd, RabbitMQ/Redis en Docker, SageMaker mediante Boto3/IAM, S3 para el artefacto y CloudWatch para observabilidad. Las unidades systemd hacen referencia a `/home/ubuntu/shopfast/.env`; ese archivo no se publicó.

La carpeta [cloud-source-candidate/](../cloud-source-candidate/) contiene snapshots sanitizados de fuentes recibidos desde EC2 y del paquete RAR. No se ha realizado una comparación byte a byte de todos los archivos con los procesos activos ni una reconstrucción completa desde cero.

## Componentes y alcance del repositorio

- `model/`: entrenamiento, métricas, dependencias y hashes del dataset.
- `prototype-local/`: API y pruebas del prototipo local.
- `cloud-source-candidate/`: fuentes cloud recuperados, Dashboard, unidades systemd y snapshot de dependencias EC2.
- `load-test/`: escenario y resultados de Locust.
- `docs/`: arquitectura, acceso AWS, evidencias, rúbrica y documentos de entrega.

## Límites conocidos

- Inventario simulado en memoria; no integra inventario comercial ni reserva unidades.
- El checkout debe continuar funcionando si falla el recomendador.
- No hay alta disponibilidad multizona demostrada.
- La API cloud recibida no muestra autenticación propia para sus rutas de entrada.
- La ruta `/api/dashboard` no incorpora autenticación propia; conservar el acceso al Dashboard por túnel SSH o añadir protección antes de exponerlo.
- El Dashboard utiliza un contexto fijo de demostración para consultar recomendaciones.
- El snapshot `pip freeze` corresponde al entorno virtual completo de EC2; no es un requirements mínimo.
- La carga Locust registrada es de baja concurrencia y loopback; no demuestra 250/750 req/s.

El Dockerfile y el Compose de la raíz corresponden al laboratorio local. No son los archivos de despliegue completos de EC2.
