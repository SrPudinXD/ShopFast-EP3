# ShopFast EP3 — resumen de entrega y estado técnico

**Asignatura:** ITY1102 — Arquitectura de Sistemas de IA  
**Fecha de consolidación documental:** 27 de noviembre de 2026  
**Equipo:** Javier Moyano, Alvaro Prieto y Martin Torres

## 1. Qué contiene la entrega académica

La versión enviada a AVA se consolidó en estos artefactos:

| Artefacto | Formato | Alcance |
|---|---|---|
| Informe técnico arc42 | PDF, 10 páginas | Arquitectura, modelo, seguridad, rendimiento, costos, riesgos y conclusión |
| Informe editable | DOCX | Fuente editable del informe |
| Presentación | PDF, 6 láminas | Resumen para exposición |
| Presentación editable | PPTX | Fuente editable de las láminas |
| Evidencias | ZIP | 305 capturas sanitizadas |
| Evidencias recientes | E93–E97 | Reinicio de API, inferencia cloud y prueba Locust |
| Código de entrenamiento | Fuente | Preparación de datos, entrenamiento, métricas y artefacto del modelo |
| Prototipo local | Fuente | API local y pruebas del prototipo |
| Código cloud candidato | Fuente y configuración | API SageMaker, RabbitMQ, consumidor Redis, Dashboard, unidades systemd y snapshot de dependencias EC2 |

Los PDF, DOCX, PPTX y ZIP de evidencias forman parte del paquete de entrega compartido por separado. El repositorio contiene el código de entrenamiento, prototipo local, documentación y snapshots sanitizados del código cloud recuperado.

## 2. Resultado del modelo

La selección se realiza por NDCG@10 de validación, no por accuracy aislada.

| Modelo | NDCG@10 validación | F1 validación |
|---|---:|---:|
| Popularidad | 0,3887 | 0,1481 |
| Regresión logística | 0,5871 | 0,3103 |
| Random Forest | **0,5939** | 0,3094 |
| XGBoost | 0,5757 | 0,3081 |

Random Forest fue seleccionado. Configuración registrada: 100 árboles, profundidad máxima 8, mínimo 10 muestras por hoja y semilla 42. Umbral binario de validación: 0,09.

En prueba, Random Forest obtuvo accuracy 0,7872, precision 0,2221, recall 0,7121, F1 0,3386 y NDCG@10 0,6453. Popularidad obtuvo NDCG@10 0,4136. El conjunto de prueba contiene 280 sesiones y 3.360 filas; 109 sesiones sin positivos no entran en el promedio NDCG.

**Interpretación:** NDCG@10 mide la calidad del orden de recomendaciones frente a los clics observados en el conjunto experimental. No demuestra aumento causal de ventas, conversión ni ticket medio.

## 3. Prueba de carga registrada

Configuración: Locust, 10 usuarios, incremento de 2 usuarios por segundo, 60 segundos, contra `127.0.0.1:8000` desde la propia EC2.

| Métrica | CSV exportado |
|---|---:|
| Solicitudes | 382 |
| Fallos | 0 |
| Throughput | 6,47 req/s |
| Promedio | 37,7 ms |
| P95 | 45 ms |
| P99 | 110 ms |
| Máximo | 161 ms |

La consola mostró 386 solicitudes y el CSV exportado 382. Se conserva el valor del CSV y se documenta la diferencia. Esta prueba acredita únicamente carga controlada de baja concurrencia en loopback. No demuestra 250/750 req/s ni latencia desde Internet.

## 4. Arquitectura documentada

- API REST con FastAPI en EC2.
- Inferencia cloud mediante AWS SageMaker.
- Random Forest local como alternativa de continuidad.
- RabbitMQ para recepción y entrega de eventos.
- Consumidor para deduplicación y procesamiento.
- Redis para persistencia de eventos y lectura del Dashboard.
- Dashboard FastAPI con frontend HTML/CSS/JavaScript recuperado desde EC2.
- S3 para el artefacto del modelo y CloudWatch para observabilidad.
- Acceso administrativo mediante túnel SSH; API y Dashboard permanecen en loopback.

El inventario del laboratorio es simulado, tiene una vigencia documentada de 300 segundos y no reserva stock ni se integra con inventario comercial. El checkout debe continuar operando si falla el recomendador.

## 5. Decisión y límites

La recomendación documentada es aplazar el lanzamiento general y mantener, como máximo, un piloto controlado con inventario vigente. No afirmar como hechos demostrados:

- incremento causal de ventas o ticket medio;
- capacidad de 250 o 750 solicitudes por segundo;
- alta disponibilidad multizona;
- TLS directo o rate limiting de producción;
- disponibilidad continua a partir de una captura puntual;
- que el prototipo local sea el mismo código desplegado en EC2.

## 6. Estado del código cloud recuperado

Se recibieron `shopfast(1).rar`, `shopfast-configuracion.tar.gz` y, posteriormente, `shopfast-dashboard-source.tar.gz`. La revisión permitió publicar snapshots sanitizados en [cloud-source-candidate/](../../cloud-source-candidate/), separados del prototipo local.

La carpeta incluye API con llamada a SageMaker y fallback local, cliente Boto3, mensajería RabbitMQ, consumidor Redis, productores de prueba, handler SageMaker, Dashboard backend/frontend, unidades systemd, versión Python 3.12.3 y un `pip freeze` de 63 paquetes del entorno virtual EC2. Se retiraron contraseñas incrustadas y no se publicaron el volcado Redis, archivos bytecode, binarios de modelo/datos ni `.env`.

Quedan brechas: la API cloud recibida no muestra autenticación propia en sus rutas de entrada; el Dashboard usa una consulta fija de demostración y su ruta `/api/dashboard` no incorpora autenticación propia; el snapshot de dependencias corresponde al entorno completo y no es un requirements mínimo. Tampoco se compararon hashes de todos los archivos con procesos activos ni se dispone del Dockerfile original de EC2. Por tanto, esta carpeta es un snapshot sanitizado recuperado desde EC2, no una prueba de despliegue reproducible de extremo a extremo.

Ver [auditoría de archivos EC2](revision-archivos-ec2.md), [brecha de código cloud](../cloud-source-gap.md), [índice de evidencias](../evidence-index.md), [checklist de rúbrica](../rubrica-checklist.md) y [guion de defensa](guion-defensa.md).
