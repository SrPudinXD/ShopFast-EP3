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
| Código de entrenamiento | ZIP / fuente | Preparación de datos, entrenamiento, métricas y artefacto del modelo |
| Prototipo local | ZIP / fuente | API local y pruebas del prototipo |

Los PDF, DOCX, PPTX y ZIP de evidencias forman parte del paquete de entrega compartido por separado. Este repositorio contiene el código de entrenamiento, métricas, prototipo local y documentación; no debe suponerse que todos los binarios del paquete AVA están publicados aquí.

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
- Redis para persistencia de eventos y lectura del dashboard.
- S3 para el artefacto del modelo y CloudWatch para observabilidad.
- Acceso administrativo mediante túnel SSH; API y dashboard permanecen en loopback.

El inventario del laboratorio es simulado, tiene una vigencia documentada de 300 segundos y no reserva stock ni se integra con inventario comercial. El checkout debe continuar operando si falla el recomendador.

## 5. Decisión y límites

La recomendación documentada es aplazar el lanzamiento general y mantener, como máximo, un piloto controlado con inventario vigente. No afirmar como hechos demostrados:

- incremento causal de ventas o ticket medio;
- capacidad de 250 o 750 solicitudes por segundo;
- alta disponibilidad multizona;
- TLS directo o rate limiting de producción;
- disponibilidad continua a partir de una captura puntual;
- que el prototipo local sea el mismo código desplegado en EC2.

## 6. Brecha de código cloud

El repositorio no contiene el conjunto íntegro de fuentes que corre en `/home/ubuntu/shopfast` ni el Dockerfile/compose original de EC2. Las capturas permiten documentar operaciones, pero no reconstruir confiablemente los archivos ausentes.

Para cerrar la brecha se debe exportar desde EC2 o desde el respaldo original, revisar y sanitizar antes de publicar: API cloud, cliente SageMaker, consumidor, dashboard, unidad systemd, dependencias, Dockerfile/compose y guía de despliegue. Excluir siempre `.env`, API Keys, claves PEM, contraseñas, tokens, credenciales AWS y logs que los contengan.

Ver también: [brecha de código cloud](../cloud-source-gap.md), [índice de evidencias](../evidence-index.md), [checklist de rúbrica](../rubrica-checklist.md) y [guion de defensa](guion-defensa.md).
