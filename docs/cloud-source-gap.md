# Brecha de código fuente cloud

El paquete seguro contiene ShopFast_EP3_API_LOCAL.zip (prototipo local con api.py, probar.py, modelo.joblib y datos) y ShopFast_EP3_modelo.zip (entrenar.py, metricas.csv, modelo.joblib y datos), además de informe, presentación, Locust y capturas.

El LEEME de la API local advierte que no incluye autenticación, TLS, broker ni persistencia duradera y que no es el código completo desplegado en AWS.

El directorio /home/ubuntu/shopfast no fue entregado como ZIP ni como conjunto íntegro de archivos fuente. Las capturas permiten verificar operaciones y fragmentos, pero no reconstruir confiablemente todos los archivos. No se etiqueta el prototipo local como versión cloud.

Para cerrar esta brecha, incorporar desde EC2 o respaldo original, sanitizando primero: api.py cloud, sagemaker_cliente.py, consumidor.py, dashboard_api.py, dashboard/index.html, styles.css, app.js, Dockerfile/compose original, unidad systemd, requirements/lockfile, instrucciones de despliegue y commit/hash.

Excluir .env, API Keys, contraseñas, claves PEM, credenciales AWS y tokens. Revisar logs e historial y rotar cualquier clave expuesta. El Dockerfile raíz de este repositorio construye solo el prototipo local; no es el Dockerfile original de AWS.
