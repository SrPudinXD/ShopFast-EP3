# Brecha del código fuente cloud

## Archivos fuente verificados
- ShopFast_EP3_API_LOCAL.zip: api.py, probar.py, modelo.joblib y ShopFast_datos.zip.
- ShopFast_EP3_modelo.zip: entrenar.py, metricas.csv, modelo.joblib y datos.
- Informe ARC42, presentación, script Locust, métricas y capturas sanitizadas.

El LEEME del paquete API local declara que no contiene autenticación, TLS, broker ni persistencia duradera; no es el código completo desplegado en AWS.

## No se recibió como fuente íntegra
El directorio EC2 /home/ubuntu/shopfast no fue entregado como ZIP o conjunto completo de archivos. Las capturas muestran operaciones y fragmentos, pero no permiten reconstruir de forma confiable todos los módulos. No se inventa ni se presenta el prototipo local como cloud.

Para cerrar esta brecha se requiere recuperar desde la instancia/respaldo, sanitizar y revisar: api.py cloud, sagemaker_cliente.py, consumidor.py, dashboard_api.py, dashboard/index.html, styles.css, app.js, Dockerfile/compose original, unidad systemd, requirements/lockfile y configuración no secreta.

Antes de copiar: excluir .env, API Keys, contraseñas, PEM y credenciales; revisar logs e historial; rotar cualquier clave expuesta; registrar commit y versión del modelo correspondiente a E93–E97.

## Estado
Pendiente. El Dockerfile de la raíz construye solo el prototipo local, no el contenedor original de AWS.