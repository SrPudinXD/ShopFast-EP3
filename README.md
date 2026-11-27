# ShopFast EP3 — ITY1102

**Asignatura:** Arquitectura de Sistemas de IA  
**Equipo:** Javier Moyano, Alvaro Prieto y Martin Torres  
**Estado:** documentación académica consolidada; piloto controlado recomendado, no producción.

## Resumen

ShopFast propone un recomendador de productos con Random Forest, FastAPI, AWS SageMaker y EC2. El flujo de eventos utiliza RabbitMQ, un consumidor y Redis; el dashboard consulta los eventos procesados.

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

## Estructura

- `model/`: entrenamiento, dependencias y métricas.
- `prototype-local/`: API y pruebas del prototipo local.
- `load-test/`: script y resultados Locust.
- `docs/`: arquitectura, acceso AWS, brecha de código cloud, rúbrica y evidencias.
- `docs/post-entrega/`: resumen de entrega, guion de defensa, manifiesto de archivos y checklist de pendientes.
- `Dockerfile`: construye el prototipo local, no la imagen original de EC2.
- `docker-compose.yml`: servicios RabbitMQ/Redis para laboratorio local.

## Reproducir entrenamiento

Extraer el archivo `ShopFast_datos.zip` del anexo académico y colocarlo en `model/ShopFast_datos.zip`:

```bash
pip install -r model/requirements.txt
python model/entrenar.py
```

El script genera `metricas.csv`, el artefacto `modelo.joblib` y gráficos de validación/prueba. Para el prototipo local, copiar `modelo.joblib` y `ShopFast_datos.zip` a `prototype-local/`.

## Ejecutar prototipo local

Requiere Python 3.12, `prototype-local/modelo.joblib` y `prototype-local/ShopFast_datos.zip`:

```bash
pip install -r prototype-local/requirements.txt
cd prototype-local
python probar.py
uvicorn api:app --host 127.0.0.1 --port 8000
```

Swagger: http://127.0.0.1:8000/docs. No exponer a Internet. Este prototipo no incluye la autenticación, TLS, broker ni persistencia duradera de la aplicación cloud; sus pruebas son locales y no deben confundirse con la evidencia de EC2.

## Arquitectura cloud documentada

Cliente → API FastAPI → validación/autorización → filtro de inventario vigente → SageMaker → ranking → respuesta JSON. La ruta de respaldo local está documentada para fallas de inferencia.

Eventos → RabbitMQ → consumidor → deduplicación → Redis → dashboard. EC2 usa IAM/Boto3 para invocar SageMaker; S3 conserva el artefacto y CloudWatch observa los servicios. El acceso administrativo se realiza por túnel SSH; API y dashboard se mantienen en loopback.

No hay alta disponibilidad multizona demostrada. Ver [arquitectura](docs/architecture.md) y [acceso seguro](docs/acceso-aws.md).

## Brecha de código fuente cloud

El código íntegro desplegado en `/home/ubuntu/shopfast` y el Dockerfile/compose original de EC2 no están incluidos en este repositorio. El Dockerfile raíz corresponde solo al prototipo local. No presentar el prototipo como código cloud. Para cerrar la brecha, exportar la fuente real desde EC2 o el respaldo original y sanitizarla antes de publicarla. Ver [detalle de la brecha](docs/cloud-source-gap.md).

## Documentación de entrega y defensa

- [Resumen de la entrega y resultados](docs/post-entrega/resumen-entrega.md)
- [Guion para defensa y demostración](docs/post-entrega/guion-defensa.md)
- [Pendientes y verificación posterior](docs/post-entrega/pendientes-y-verificacion.md)
- [Manifiesto SHA-256 de los artefactos](docs/post-entrega/manifesto-artefactos.md)
- [Checklist de rúbrica](docs/rubrica-checklist.md)
- [Índice de evidencias](docs/evidence-index.md)

Los PDF, DOCX, PPTX y ZIP de capturas se conservaron en el paquete de entrega compartido por AVA; no están versionados como binarios en este repositorio. El manifiesto permite verificar su integridad cuando se copien a un respaldo o release.

## Seguridad

No publicar `.env`, API Keys, claves PEM, contraseñas, tokens, credenciales AWS ni logs que los contengan. Una captura con API Key fue excluida del paquete sanitizado; si la clave estuvo activa o fue expuesta por otro medio, rotarla. No publicar puertos internos de API, RabbitMQ o Redis directamente en Internet.

## Decisión

Se recomienda aplazar el lanzamiento general y permitir únicamente un piloto controlado con inventario vigente. No afirmar como demostrados: impacto causal en ventas, 250/750 req/s, alta disponibilidad multizona, TLS directo, rate limiting de producción ni código cloud íntegro.
