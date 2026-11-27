# ShopFast EP3 — pendientes y verificación posterior a la entrega

Este documento separa lo demostrado, lo documentado y lo que todavía requiere trabajo. No convierte evidencia histórica en una garantía de disponibilidad actual.

## Estado

| Área | Estado | Próximo paso |
|---|---|---|
| Informe arc42 | Preparado y enviado por AVA | Conservar PDF y fuente DOCX |
| Presentación | Preparada y enviada por AVA | Conservar PDF y fuente PPTX |
| Entrenamiento | Código y métricas en el repositorio | Reproducir con el dataset original |
| Prototipo local | Código y pruebas publicados | Mantener separado del código cloud candidato |
| API con SageMaker | Fuente candidata recibida y sanitizada | Comparar hashes con EC2 y validar autenticación |
| RabbitMQ/Redis | Productor, consumidor y Compose recibidos | Probar con credenciales nuevas en entorno controlado |
| systemd | Unidades API, consumidor y Dashboard recibidas | Validar configuración y dependencias |
| Dashboard | Backend y frontend recuperados desde EC2 | Probar integración con Redis y API en entorno controlado |
| Dependencias cloud | Snapshot `pip freeze` de EC2 recuperado | Definir requirements mínimo reproducible |
| Inferencia SageMaker | Evidencia histórica E94 y cliente recibido | Repetir smoke test autorizado si el endpoint sigue activo |
| Locust | Ensayo de 10 usuarios registrado | Ejecutar mayor concurrencia solo con capacidad y autorización |
| Evidencias | 305 imágenes sanitizadas en el paquete de entrega | Mantener ZIP separado; revisar antes de publicar |
| Autenticación API Key | No aparece en `api.py` recibido | Verificar proxy o middleware externo |
| Artefactos binarios | Excluidos por .gitignore | Publicar solo en un canal de artefactos aprobado si hace falta |
| Seguridad | Copia publicada sin contraseñas embebidas | Rotar credenciales si los valores originales estuvieron activos |

## Lista para completar la fuente cloud

- [x] Recibir API, cliente SageMaker, mensajería y consumidor.
- [x] Recibir unidades systemd de API, consumidor y Dashboard.
- [x] Recuperar `dashboard_api.py` y los recursos estáticos desde EC2.
- [x] Obtener versión Python y snapshot `pip freeze` del entorno EC2.
- [x] Publicar una copia candidata separada del prototipo local.
- [x] Retirar contraseñas embebidas de la copia publicada.
- [ ] Recuperar Dockerfile y configuración completa de despliegue de EC2, si existen.
- [ ] Definir dependencias mínimas y reproducibles separadas del snapshot completo.
- [ ] Verificar dónde se aplica autenticación API Key, si existe fuera de la API.
- [ ] Comparar los archivos con el filesystem activo de EC2.
- [ ] Revisar la consulta fija del Dashboard y decidir si se mantiene solo para demostración o se parametriza.
- [ ] Añadir instrucciones reproducibles de despliegue y rollback.
- [ ] Ejecutar pruebas integradas y guardar evidencias nuevas.
- [ ] Registrar el hash del commit que representa el despliegue verificado.

## Reglas de publicación

Nunca publicar:
- `.env`, claves PEM o claves privadas;
- API Keys, tokens, contraseñas o credenciales AWS;
- logs con cabeceras de autorización, cookies o identificadores personales;
- volcados de Redis con eventos runtime;
- archivos `.pyc` o carpetas `__pycache__`.

No cambiar el Dockerfile del prototipo local para hacerlo pasar por el Dockerfile de EC2. Conservar ambas fuentes con nombres y documentación inequívocos.

## Revisión de resultados

- NDCG@10 y F1 son métricas del conjunto experimental, no métricas de negocio.
- La prueba Locust es de baja concurrencia y loopback; no acredita el objetivo de capacidad.
- Los costos son estimaciones de referencia, no una factura final.
- La disponibilidad observada en una captura es puntual, no un SLO medido.
- Los umbrales de rollback documentados son propuestas operativas, no una prueba de rollback ejecutado.
