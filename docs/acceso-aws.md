# Acceso autorizado al laboratorio AWS

Las capturas y el informe documentan túneles SSH desde Windows hacia EC2. La instancia usa API y dashboard en loopback; no abrir esos puertos directamente a Internet.

Reemplaza los marcadores por una clave privada autorizada y la IP/DNS pública vigente de la consola AWS:

```bash
ssh -i <RUTA_CLAVE_PEM> -L 8001:127.0.0.1:8000 -L 8081:127.0.0.1:8080 ubuntu@<IP_O_DNS_PUBLICO_EC2>
```

Con el túnel activo:
- API/Swagger: http://127.0.0.1:8001/docs
- Dashboard: http://127.0.0.1:8081

No subir claves PEM, contraseñas, API Keys, tokens ni .env. Mantener la API Key en configuración local de EC2 y rotarla si fue expuesta. RabbitMQ y Redis no deben quedar publicados en interfaces públicas. Los enlaces localhost solo funcionan mientras el túnel SSH esté activo.
