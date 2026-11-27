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
- `cloud-source-candidate/`: copia candidata sanitizada de la API con SageMaker, cliente Boto3, RabbitMQ, consumidor Redis, handler de inferencia, pruebas y unidades systemd recibidas después.
- `load-test/`: script y resultados Locust.
- `docs/`: arquitectura, acceso AWS, brecha de código cloud, rúbrica y evidencias.
- `docs/post-entrega/`: resumen de entrega, guion de defensa, manifiesto de archivos, auditoría de archivos EC2 y checklist de pendientes.
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

## Código cloud candidato

La carpeta `cloud-source-candidate/` contiene los fuentes recibidos en `shopfast(1).rar` y las unidades systemd de `shopfast-configuracion.tar.gz`, revisados y sanitizados. Se retiraron contraseñas incrustadas y se trasladó la configuración de conexión a variables de entorno.

**No equivale a un despliegue verificado:** falta `dashboard_api.py` y sus recursos estáticos; la API Key no aparece implementada en el `api.py` recibido; las versiones exactas de Boto3/Pika/Redis no venían en el paquete; y no se compararon los archivos con procesos activos de EC2. Los binarios de modelo/datos, el volcado Redis y los archivos `.pyc` no se publicaron.

Ver [auditoría de archivos EC2](docs/post-entrega/revision-archivos-ec2.md), [brecha restante](docs/cloud-source-gap.md) y [arquitectura](docs/architecture.md).

## Documentación de entrega y defensa

- [Resumen de la entrega y resultados](docs/post-entrega/resumen-entrega.md)
- [Guion para defensa y demostración](docs/post-entrega/guion-defensa.md)
- [Auditoría de los archivos EC2 recibidos](docs/post-entrega/revision-archivos-ec2.md)
- [Pendientes y verificación posterior](docs/post-entrega/pendientes-y-verificacion.md)
- [Manifiesto SHA-256 de los artefactos](docs/post-entrega/manifiesto-artefactos.md)
- [Checklist de rúbrica](docs/rubrica-checklist.md)
- [Índice de evidencias](docs/evidence-index.md)

Los PDF, DOCX, PPTX y ZIP de capturas se conservaron en el paquete de entrega compartido por AVA; no están versionados como binarios en este repositorio. El manifiesto permite verificar su integridad cuando se copien a un respaldo o release.

## Seguridad

No publicar `.env`, API Keys, claves PEM, contraseñas, tokens, credenciales AWS ni logs que los contengan. No publicar puertos internos de API, RabbitMQ o Redis directamente en Internet. Si las credenciales de prueba que aparecían en el RAR original se utilizaron en EC2, rotarlas.

## Decisión

Se recomienda aplazar el lanzamiento general y permitir únicamente un piloto controlado con inventario vigente. No afirmar como demostrados: impacto causal en ventas, 250/750 req/s, alta disponibilidad multizona, TLS directo, rate limiting de producción, autenticación API Key en la copia recibida ni despliegue cloud reproducible de extremo a extremo.
