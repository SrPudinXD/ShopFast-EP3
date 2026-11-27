# Revisión de rúbrica EP3 AS IA

| Criterio | Peso | Estado | Observación |
|---|---:|---|---|
| IE1 — Modelo cloud con endpoint consumible | 10% | Demostrado en laboratorio | E42/E47 y E94 muestran inferencia cloud y HTTP 200. |
| IE2 — Integración empresarial e interpretabilidad | 10% | Parcial | API y dashboard existen; falta conciliación integral del mismo ID, versión, filtrado y estado visible. |
| IE4 — SageMaker, escalabilidad y costos | 5% | Parcial | Hay estimación de costos y Locust de baja concurrencia; no se demuestra 250/750 req/s. |
| IE5 — Infraestructura mínima, modelo, dataset y dashboard | 5% | Demostrado en laboratorio | EC2, modelo, dataset y dashboard documentados; inventario simulado. |
| IE7 — REST, interoperabilidad y seguridad | 10% | Parcial | API Key, IAM y SSH restringido; TLS directo y rate limiting de producción no acreditados. |
| IE10 — Pruebas funcionales y rendimiento | 10% | Parcial | Matriz de 12 casos y Locust controlado; faltan pruebas automatizadas reproducibles con commit, entrada y aserción previa. |
| IE3 — Defensa de despliegue y decisión empresarial | 10% | Pendiente | Se evalúa en defensa. |
| E6 — Defensa de plataforma AIaaS, rendimiento, costo y flexibilidad | 10% | Pendiente | Distinguir medición propia, tarifa de referencia y proyección. |
| IE8 — Defensa de integración y arquitectura | 5% | Pendiente | Explicar SageMaker, fallback, broker y Redis. |
| IE9 — Demostración en vivo | 5% | Pendiente | Requiere predicción nueva, invocación real y traza hasta dashboard/consumidor. |
| IE11 — Validación y optimización | 5% | Pendiente | Explicar selección por NDCG@10 y límites de carga. |
| IE12 — Lenguaje técnico y formal | 5% | Pendiente | Se evalúa durante exposición. |
| IE13 — Respuestas al docente | 10% | Pendiente | No se certifica solo con documentos. |

## Brechas reconocidas
Contrato móvil, caso formal de frontera, rollback de artefacto incompatible, prueba de estrés, conciliación endpoint-dashboard, TLS directo, rate limiting, RPO de zona y código exacto del despliegue AWS.

Locust: 10 usuarios, incremento 2 usuarios/s, 60 s, loopback en EC2. CSV: 382 solicitudes, 0 fallos, 6,47 req/s, promedio 37,7 ms, P95 45 ms, P99 110 ms, máximo 161 ms. No afirmar validación de 250/750 req/s.
