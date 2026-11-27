# Checklist rúbrica EP3 AS IA

Estados según informe, anexo y evidencias disponibles; parcial/pendiente no equivale a cumplimiento completo.

| Criterio | Peso | Estado documentado |
|---|---:|---|
| IE1 modelo cloud y endpoint | 10% | Demostrado en laboratorio; E42/E47/E94 |
| IE2 integración empresarial e interpretabilidad | 10% | Parcial: falta conciliación integral ID/versión/filtro/dashboard |
| IE4 SageMaker, escalabilidad y costos | 5% | Parcial: Locust de 10 usuarios; no demuestra 250/750 req/s |
| IE5 infraestructura, modelo, dataset y dashboard | 5% | Demostrado en laboratorio; inventario simulado |
| IE7 REST, interoperabilidad y seguridad | 10% | Parcial: TLS directo y rate limiting de producción no acreditados |
| IE10 pruebas funcionales y rendimiento | 10% | Parcial: matriz retrospectiva y Locust; faltan pruebas automatizadas reproducibles |
| IE3 defensa de estrategia | 10% | Pendiente de defensa |
| E6 defensa AIaaS, costo y flexibilidad | 10% | Pendiente de defensa |
| IE8 defensa de arquitectura | 5% | Pendiente de defensa |
| IE9 demostración en vivo | 5% | Pendiente de demostración |
| IE11 validación y optimización | 5% | Pendiente de defensa |
| IE12 lenguaje técnico | 5% | Pendiente de defensa |
| IE13 respuestas al docente | 10% | Pendiente de defensa |

## Brechas reconocidas
Contrato móvil; caso formal de frontera; rollback de artefacto incompatible; estrés a capacidad objetivo; conciliación endpoint/dashboard; TLS y rate limiting; RPO de zona no demostrable; código exacto cloud y Dockerfile original no recuperados.

## Locust
10 usuarios, spawn 2 usuarios/s, 60 s, loopback en EC2. CSV: 382 solicitudes, 0 fallos, 6,47 req/s, promedio 37,7 ms, P95 45 ms, P99 110 ms, máximo 161 ms. No afirmar 250/750 req/s.