# Resultados Locust registrados

Configuración: GET /v1/recommendations contra http://127.0.0.1:8000 (loopback dentro de EC2), 10 usuarios, incremento 2 usuarios/s, 60 segundos.

CSV exportado:
- 382 solicitudes, 0 fallos, 6,47 solicitudes/s.
- Promedio 37,7 ms; P50 36 ms; P90 40 ms; P95 45 ms; P98 52 ms; P99 110 ms; P99.9 160 ms; máximo 161 ms.

La consola mostró 386 solicitudes; el CSV exportado registró 382. El informe conserva el total persistido del CSV y declara la diferencia.

La prueba demuestra comportamiento bajo carga controlada de baja concurrencia. No demuestra 250 ni 750 solicitudes/s y no mide latencia desde Internet. No extrapolar a producción.

E93: reinicio API y respuesta inicial. E94: inferencia SageMaker HTTP 200, rf-cloud-v1 y fallback=false. E95: instalación Locust. E96: resumen y percentiles. E97: CSV exportado.

El script Locust requiere SHOPFAST_API_KEY y está destinado a la API cloud autenticada; no funciona sin cambios contra prototype-local/api.py, que no implementa autenticación.
