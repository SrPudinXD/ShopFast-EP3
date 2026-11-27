# Resultados Locust registrados

- Endpoint: GET /v1/recommendations
- Destino: http://127.0.0.1:8000 (loopback dentro de EC2)
- Usuarios: 10; incremento: 2 usuarios/s; duración: 60 segundos.
- CSV: 382 solicitudes, 0 fallos, 6,47 solicitudes/s.
- Promedio: 37,7 ms; P50: 36 ms; P90: 40 ms; P95: 45 ms; P98: 52 ms; P99: 110 ms; P99.9: 160 ms; máximo: 161 ms.
- La consola mostró 386 solicitudes; el CSV exportado 382. Se conserva el total del CSV persistido y se declara la diferencia.

La prueba demuestra comportamiento bajo carga controlada de baja concurrencia. No demuestra 250/750 req/s ni mide latencia desde Internet. Locust apuntó a loopback dentro de EC2.

E93: reinicio API y respuesta inicial. E94: inferencia SageMaker HTTP 200, rf-cloud-v1 y fallback=false. E95: instalación Locust. E96: resumen y percentiles. E97: CSV exportado.

El script Locust requiere SHOPFAST_API_KEY y está destinado a la API cloud autenticada; no funciona sin cambios contra el prototipo local, que no implementa autenticación.