# ShopFast EP3 — pendientes y verificación posterior a la entrega

Este documento separa lo demostrado, lo documentado y lo que todavía requiere trabajo. No convierte evidencia histórica en una garantía de disponibilidad actual.

## Estado

| Área | Estado | Próximo paso |
|---|---|---|
| Informe arc42 | Preparado y enviado por AVA | Conservar PDF y fuente DOCX |
| Presentación | Preparada y enviada por AVA | Conservar PDF y fuente PPTX |
| Entrenamiento | Código y métricas en el repositorio | Reproducir con el dataset original |
| Prototipo local | Código y pruebas publicados | Mantener claramente separado del despliegue cloud |
| Inferencia SageMaker | Evidencia de HTTP 200 | Repetir demostración en vivo si la instancia está activa |
| Locust | Ensayo de 10 usuarios registrado | Ejecutar prueba de mayor concurrencia solo con capacidad y autorización |
| Evidencias | 305 imágenes sanitizadas en el paquete de entrega | Mantener ZIP separado; revisar antes de publicar |
| Código cloud EC2 | Incompleto en el repositorio | Exportar fuente original y configuración sanitizada |
| Seguridad | No publicar secretos | Revisar archivos, historial y capturas; rotar cualquier credencial expuesta |

## Lista para completar la fuente cloud

- [ ] Exportar la API que realmente corre en EC2.
- [ ] Exportar el cliente de SageMaker.
- [ ] Exportar el consumidor RabbitMQ.
- [ ] Exportar la API y los recursos estáticos del dashboard.
- [ ] Exportar unidad systemd y configuración de servicios.
- [ ] Exportar Dockerfile y docker-compose originales.
- [ ] Exportar requirements o lockfile.
- [ ] Añadir instrucciones reproducibles de despliegue y rollback.
- [ ] Retirar secretos y datos sensibles.
- [ ] Revisar los archivos antes de hacer commit.
- [ ] Registrar el hash del commit que representa el despliegue.

## Reglas de publicación

Nunca publicar:
- `.env`, claves PEM o claves privadas;
- API Keys, tokens, contraseñas o credenciales AWS;
- logs con cabeceras de autorización, cookies o identificadores personales;
- capturas que muestren credenciales activas.

No cambiar el Dockerfile del prototipo local para hacerlo pasar por el Dockerfile de EC2. Conservar ambos con nombres y documentación inequívocos.

## Revisión de resultados

- NDCG@10 y F1 son métricas del conjunto experimental, no métricas de negocio.
- La prueba Locust es de baja concurrencia y loopback; no acredita el objetivo de capacidad.
- Los costos son estimaciones de referencia, no una factura final.
- La disponibilidad observada en una captura es puntual, no un SLO medido.
- Los umbrales de rollback documentados son propuestas operativas, no una prueba de rollback ejecutado.
