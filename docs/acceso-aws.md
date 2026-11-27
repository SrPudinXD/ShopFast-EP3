# Acceso autorizado AWS

Las capturas documentan túneles SSH desde Windows a EC2. La API y el dashboard se sirven en loopback; no abrir esos puertos directamente a Internet.

Sustituye los marcadores por una clave autorizada y la IP/DNS pública vigente desde la consola AWS:
```bash
ssh -i <RUTA_CLAVE_PEM> -L 8001:127.0.0.1:8000 -L 8081:127.0.0.1:8080 ubuntu@<IP_O_DNS_PUBLICO_EC2>
```
Con el túnel activo:
- Swagger: http://127.0.0.1:8001/docs
- Dashboard: http://127.0.0.1:8081

No publicar claves PEM, API Keys, tokens, contraseñas ni credenciales AWS. Los enlaces locales funcionan solo mientras el túnel autorizado esté activo. No son URLs públicas de producción.