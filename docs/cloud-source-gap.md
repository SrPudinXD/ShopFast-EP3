# Estado del código cloud recibido y brechas pendientes

## Material recibido

Se revisaron tres archivos compartidos para completar la fuente ShopFast:

- `shopfast(1).rar`: contiene API, cliente SageMaker, mensajería RabbitMQ, consumidor Redis, productores de prueba, handler de inferencia, dependencias, pruebas y artefactos del modelo/datos.
- `shopfast-configuracion.tar.gz`: contiene las unidades systemd de API, consumidor y dashboard, además de un volcado Redis.
- `shopfast-dashboard-source.tar.gz`: exportación creada desde `/home/ubuntu/shopfast` en EC2 el 27-11-2026; contiene el backend y frontend del Dashboard, `pip freeze`, versión Python y salida de `systemctl cat`.

Se publicó una copia de código sanitizada y separada del prototipo local en [cloud-source-candidate/](../cloud-source-candidate/). No se reemplazó `prototype-local/`.

## Qué se incorporó

- `api.py`: intenta inferencia SageMaker y usa Random Forest local como respaldo.
- `sagemaker_cliente.py`: cliente Boto3 para el endpoint.
- `mensajeria.py`: publicación durable en RabbitMQ.
- `consumidor.py`: deduplicación por fuente + ID y escritura Redis antes del ACK.
- Productores y consumidor de recuperación para pruebas.
- Handler de inferencia SageMaker y sus dependencias.
- Compose sanitizado y unidades systemd.
- Scripts y resultados de pruebas locales.
- Plantilla de variables de entorno sin credenciales.
- `dashboard_api.py`, `dashboard/index.html`, `dashboard/app.js` y `dashboard/styles.css` recuperados desde el directorio de trabajo EC2.
- `python-version-ec2.txt` con Python 3.12.3 y `requirements-ec2-freeze-2026-11-27.txt` con el snapshot de 63 paquetes del entorno virtual.

La configuración de SageMaker y RabbitMQ se hizo configurable por variables de entorno en la copia publicada. Las contraseñas incrustadas en scripts/Compose fueron retiradas. Si alguna credencial del archivo original se utilizó en EC2, debe rotarse.

## Diferencias verificadas y brechas

1. **Dashboard recuperado:** la unidad `shopfast-dashboard.service` ejecuta `dashboard_api:app`; se recuperaron el backend y los tres recursos estáticos. El servicio se configuró para escuchar en `127.0.0.1:8080`.
2. **Autenticación:** el `api.py` candidato recibido no contiene middleware, dependencia ni validación de API Key en sus rutas de entrada. El Dashboard obtiene `SHOPFAST_API_KEY` desde el entorno del proceso y la usa en la cabecera `X-API-Key` al invocar el motor local de recomendaciones. La ruta `/api/dashboard` no incorpora autenticación propia en este módulo. No afirmar que todas las rutas están protegidas.
3. **Dependencias:** el `requirements.txt` original no declaraba todos los paquetes importados por los módulos cloud. El nuevo `pip freeze` es un snapshot del entorno virtual completo de EC2, no una lista mínima del Dashboard ni una receta reproducible por sí sola.
4. **Configuración no entregada:** las unidades de servicio hacen referencia a `/home/ubuntu/shopfast/.env`, pero ese archivo no fue incluido y no se publica.
5. **Inventario simulado:** el código mantiene stock en memoria, inicializa P17/P28 con cantidades de laboratorio y aplica vencimiento de 300 segundos. No integra inventario comercial ni reserva unidades.
6. **Consulta de demostración fija:** el endpoint de recomendaciones del Dashboard utiliza `subject_ref=U7`, contexto `audio`, límite 5 y superficie `home`; no recibe contexto dinámico del usuario.
7. **Proveniencia:** el Dashboard se copió desde el directorio de trabajo configurado en systemd. No se compararon hashes de todos los archivos con procesos ya cargados en memoria ni se registró un hash de despliegue previo. Se etiqueta como snapshot exportado desde EC2, no como verificación del estado actual de cada proceso.
8. **Pruebas:** `pruebas_locales.json` contiene diez resultados OK aportados por el paquete. No se ejecutaron de nuevo en este entorno ni demuestran disponibilidad AWS actual.

## Archivos excluidos deliberadamente

- `.env`, contraseñas y secretos.
- Archivos `.pyc` y `__pycache__/`.
- `redis-dump.rdb`, porque es estado runtime con eventos de prueba, no fuente reproducible.
- `modelo.joblib`, `model.tar.gz` y `ShopFast_datos.zip`, porque el repositorio los excluye por `.gitignore` y son artefactos binarios/datos. El ZIP de datos sí pasó sus nueve verificaciones SHA-256 internas; el modelo dentro de `model.tar.gz` coincide con `modelo.joblib` del mismo archivo.

## Próximos pasos para cerrar la brecha

- Recuperar el Dockerfile y configuración completa de despliegue de EC2, si existen.
- Obtener el `.env` solo en EC2 para inventariar nombres de variables, sin copiar sus valores a GitHub.
- Definir dependencias mínimas y reproducibles separadas del snapshot `pip freeze`.
- Confirmar si la API Key se aplica en un proxy, middleware externo o en otro archivo no entregado.
- Comparar hashes de los fuentes con los archivos del servidor y registrar el commit/despliegue.
- Revisar la consulta fija del Dashboard y decidir si se mantiene solo para demostración o se parametriza.
- Ejecutar pruebas integradas autorizadas y documentar sus resultados reales.

No etiquetar el Dockerfile raíz como Dockerfile de EC2: ese archivo sigue construyendo únicamente el prototipo local.
