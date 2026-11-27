# ShopFast EP3 — guion breve para defensa y demostración

## 1. Apertura

“ShopFast propone una arquitectura de recomendación para mostrar hasta diez productos en inicio y ficha. La solución combina un modelo de ranking, una API REST y servicios cloud. El objetivo de esta evaluación es demostrar el flujo técnico y reconocer qué resultados todavía no permiten una puesta en producción.”

## 2. Explicar la arquitectura

1. El cliente solicita recomendaciones a FastAPI.
2. La API valida la solicitud y filtra productos con inventario conocido y vigente.
3. La inferencia principal se realiza en SageMaker.
4. Si la inferencia cloud falla, existe una ruta de respaldo local documentada.
5. Los eventos se publican en RabbitMQ, los procesa un consumidor y se persisten en Redis.
6. El dashboard consulta los eventos procesados.

Aclaración importante: el inventario usado en el laboratorio es simulado. No existe reserva de stock ni integración comercial real.

## 3. Justificar el modelo

“Comparamos Popularidad, Regresión logística, Random Forest y XGBoost. Elegimos Random Forest porque obtuvo el mejor NDCG@10 de validación: 0,5939. En prueba alcanzó NDCG@10 de 0,6453, frente a 0,4136 de Popularidad. Esta métrica evalúa el orden de los productos frente a los clics observados; no equivale a conversión ni demuestra ventas incrementales.”

Configuración registrada: 100 árboles, profundidad 8, mínimo 10 muestras por hoja y semilla 42.

## 4. Presentar las pruebas operativas

- Inferencia cloud: evidencia E94, HTTP 200, modelo rf-cloud-v1 y fallback=false.
- Recuperación: E93–E94 documentan reinicio de API y respuesta cloud posterior.
- Locust: 10 usuarios durante 60 segundos, 382 solicitudes en CSV, 0 fallos, promedio 37,7 ms y P95 45 ms.
- El ensayo se ejecutó desde EC2 contra loopback. No extrapolarlo a 250/750 solicitudes por segundo.

## 5. Demostración sugerida

Antes de comenzar, comprobar que la instancia esté activa y que la clave privada se encuentre localmente. No mostrar ni compartir la clave, API Key, variables de entorno o credenciales.

1. Abrir el túnel SSH autorizado.
2. Mostrar Swagger mediante el túnel local.
3. Ejecutar una solicitud de recomendación con un usuario de prueba.
4. Explicar el modo de inferencia y la versión del modelo devueltos.
5. Si está disponible el flujo de eventos, seguir un ID de prueba hasta el consumidor/Redis/dashboard.
6. Mostrar una métrica del modelo y una métrica operativa, explicando sus diferencias.

No presentar como demostración en vivo una captura histórica. Si un servicio no está disponible, decirlo y usar la evidencia registrada identificándola como evidencia previa.

## 6. Seguridad, continuidad y decisión

- No publicar puertos internos de API, RabbitMQ o Redis directamente en Internet.
- Mantener el acceso administrativo por SSH.
- Si el inventario no está verificado o está vencido, excluir el producto.
- Si falla el recomendador, el checkout debe seguir disponible.
- La recomendación es aplazar el lanzamiento general y limitarse a un piloto controlado.

## 7. Preguntas que se deben poder responder

**¿Por qué Random Forest?** Porque logró el mayor NDCG@10 de validación entre los modelos comparados.

**¿Por qué no basta con accuracy?** Porque el objetivo principal es ordenar productos relevantes; NDCG@10 evalúa la calidad del ranking.

**¿El modelo aumenta las ventas?** No se ha demostrado causalidad. Se necesita un experimento controlado por usuario y medir compras.

**¿La prueba Locust valida 750 req/s?** No. Solo midió 10 usuarios y 6,47 req/s en loopback.

**¿El inventario es real?** No, es simulado y no reserva unidades.

**¿La arquitectura tiene alta disponibilidad multizona?** No está demostrada; EC2 y el endpoint constituyen puntos únicos de falla.

**¿El repositorio contiene todo el código desplegado?** Contiene entrenamiento, prototipo local y una copia candidata sanitizada de la exportación EC2. No se ha verificado contra procesos activos y falta el dashboard.

**¿La API recibida valida una API Key?** No aparece esa validación en el módulo api.py recibido. Se debe comprobar si está en un proxy o middleware externo antes de afirmarlo.
