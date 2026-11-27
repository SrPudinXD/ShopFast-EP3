# ShopFast EP3 — ITY1102

**Asignatura:** Arquitectura de Sistemas de IA  
**Equipo:** Javier Moyano, Alvaro Prieto y Martin Torres  
**Estado:** documentación académica consolidada; piloto controlado recomendado, no producción.

## Resumen

ShopFast propone un recomendador de productos con Random Forest, FastAPI, AWS SageMaker y EC2. El flujo de eventos utiliza RabbitMQ, un consumidor y Redis; el Dashboard consulta los eventos procesados.

**Límite esencial:** el inventario usado en el laboratorio es simulado. No existe integración comercial ni reserva de stock. El checkout debe continuar funcionando si falla el recomendador.

## Resultados del modelo

La selección se realiza por NDCG@10 de validación:

| Modelo | NDCG@10 validación | F1 validación |
|---|---:|---:|
| Popularidad | 0.3887 | 0.1481 |
| Regresión logística | 0.5871 | 0.3103 |
| Random Forest | **0.5939** | 0.3094 |
| XGBoost | 0.5757 | 0.3081 |

Random Forest se seleccionó con 100 árboles, profundidad máxima 8, mínimo 10 muestras por hoja y semilla 42. En prueba obtuvo NDCG@10 0.6453 y F1 0.3386. Popularidad obtuvo NDCG@10 0.4136. NDCG mide la calidad del ranking frente a clics observados; no demuestra ventas ni conversión causal. Ver [métricas](model/metricas.csv) y [código de entrenamiento](model/entrenar.py).

## Prueba de carga documentada

Locust: 10 usuarios, incremento 2 usuarios/s, 60 s, contra `127.0.0.1:8000` desde EC2. CSV exportado: 382 solicitudes, 0 fallos, 6.47 req/s, promedio 37.7 ms, P95 45 ms, P99 110 ms y máximo 161 ms. La consola mostró 386 solicitudes; se conserva el total CSV y se deja constancia de la diferencia.

Esta prueba es de baja concurrencia y loopback. No demuestra 250/750 req/s ni latencia desde Internet. Ver [resultados Locust](load-test/Resultados_Locust_LEER.md).

## Estructura del repositorio

- `model/`: entrenamiento, dependencias, métricas y hashes del dataset.
- `prototype-local/`: API y pruebas del prototipo local.
- `cloud-source-candidate/`: snapshot sanitizado de API cloud, SageMaker, RabbitMQ/Redis, Dashboard, unidades systemd y entorno EC2.
- `load-test/`: script y resultados Locust.
- `docs/`: arquitectura, acceso AWS, evidencias, rúbrica y documentación de entrega.
- `Dockerfile` y `docker-compose.yml` de la raíz: entorno de laboratorio local, no despliegue original de EC2.

## Reproducir entrenamiento

Extraer el archivo `ShopFast_datos.zip` del anexo académico y colocarlo en `model/ShopFast_datos.zip`:

```bash
pip install -r model/requirements.txt
python model/entrenar.py
```

El script genera métricas, el artefacto `model/modelo.joblib` y gráficos de validación/prueba. Los datos y artefactos binarios no se versionan en este repositorio; revisar [model/SHA256.txt](model/SHA256.txt) para los hashes de los CSV originales.

Para ejecutar el prototipo local con ese resultado, copia el dataset y el modelo a su carpeta (no se suben a Git):
```bash
cp model/ShopFast_datos.zip prototype-local/ShopFast_datos.zip
cp model/modelo.joblib prototype-local/modelo.joblib
```

## Servicios locales de laboratorio

El Compose de la raíz inicia RabbitMQ y Redis para pruebas locales. Copia `.env.example` a `.env`, cambia la contraseña de ejemplo y ejecuta:

```bash
docker compose up -d
```

Los puertos quedan ligados a `127.0.0.1`; no publiques estos servicios directamente en Internet. Para detenerlos: `docker compose down`.

## Ejecutar prototipo local

Requiere Python 3.12, `prototype-local/modelo.joblib` y `prototype-local/ShopFast_datos.zip`:

```bash
pip install -r prototype-local/requirements.txt
cd prototype-local
python probar.py
uvicorn api:app --host 127.0.0.1 --port 8000
```

Swagger: http://127.0.0.1:8000/docs. No exponer a Internet. Este prototipo no incluye la autenticación, TLS, broker ni persistencia duradera de la aplicación cloud; sus pruebas son locales y no deben confundirse con la evidencia de EC2.

Para construir la imagen local, primero copia `modelo.joblib` y `ShopFast_datos.zip` a `prototype-local/` (son artefactos locales ignorados por Git) y ejecuta:

```bash
docker build -t shopfast-local .
docker run --rm -p 127.0.0.1:8000:8000 shopfast-local
```

La imagen escucha dentro del contenedor en el puerto 8000 y se publica solo en loopback del equipo anfitrión.

## Código cloud recuperado

La carpeta `cloud-source-candidate/` contiene snapshots sanitizados de los archivos recibidos en `shopfast(1).rar`, `shopfast-configuracion.tar.gz` y `shopfast-dashboard-source.tar.gz`. El Dashboard incluye `dashboard_api.py` y sus recursos HTML/CSS/JS. También se recuperó la versión Python 3.12.3 y un `pip freeze` de 63 paquetes del entorno virtual completo de EC2.

**No equivale a un despliegue verificado y reproducible:** falta el Dockerfile original de EC2; el `pip freeze` es un snapshot del entorno completo, no un requirements mínimo; no se compararon los hashes de todos los archivos con procesos activos; la API candidata no muestra autenticación propia de sus rutas de entrada; y la ruta `/api/dashboard` no incorpora autenticación propia. El Dashboard usa `SHOPFAST_API_KEY` para llamar al motor interno, pero esa protección no se extiende automáticamente a todas las rutas. Los binarios de modelo/datos, el volcado Redis, `.env`, claves PEM y archivos `.pyc` no se publicaron.

Ver [auditoría de archivos EC2](docs/post-entrega/revision-archivos-ec2.md), [documentación del Dashboard](cloud-source-candidate/dashboard/README.md), [brechas cloud pendientes](docs/cloud-source-gap.md) y [arquitectura](docs/architecture.md).

## Revisión técnica propuesta

- [Revisión de seguridad y compatibilidad cloud](docs/security-review.md)
- [Workflow de pruebas automatizadas](.github/workflows/tests.yml) — ejecuta las pruebas de seguridad en Python 3.12 al abrir o actualizar un PR hacia `main`.

La rama `review/cloud-hardening` contiene cambios propuestos y pruebas unitarias; `main` conserva el snapshot previo. No desplegar esa rama en EC2 sin completar las comprobaciones indicadas en la revisión.

## Documentación de entrega y defensa

- [Resumen de entrega y resultados](docs/post-entrega/resumen-entrega.md)
- [Defensa y demostración](docs/post-entrega/guion-defensa.md)
- [Auditoría de los archivos EC2](docs/post-entrega/revision-archivos-ec2.md)
- [Pendientes y verificación posterior](docs/post-entrega/pendientes-y-verificacion.md)
- [Manifiesto SHA-256 de artefactos](docs/post-entrega/manifiesto-artefactos.md)
- [Checklist](docs/rubrica-checklist.md)
- [Índice de evidencias](docs/evidence-index.md)
- [Acceso seguro al laboratorio AWS](docs/acceso-aws.md)

Los PDF, DOCX, PPTX y ZIP de capturas se conservaron en el paquete de entrega compartido por AVA; no están versionados como binarios en este repositorio. El manifiesto permite verificar su integridad cuando se copien a un respaldo o release.

## Seguridad

No publicar `.env`, API Keys, claves PEM, contraseñas, tokens, credenciales AWS ni logs que los contengan. No publicar puertos internos de API, RabbitMQ o Redis directamente en Internet. Si las credenciales de prueba que aparecían en el RAR original se utilizaron en EC2, rotarlas.

## Decisión

Se recomienda aplazar el lanzamiento general y permitir únicamente un piloto controlado con inventario vigente. No afirmar como demostrados: impacto causal en ventas, 250/750 req/s, alta disponibilidad multizona, TLS directo, rate limiting de producción, autenticación API Key en la copia recibida ni despliegue cloud reproducible de extremo a extremo.
