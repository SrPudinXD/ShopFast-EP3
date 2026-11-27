# Imagen del prototipo local; no corresponde al despliegue original de EC2.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY prototype-local/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

COPY prototype-local/api.py /app/api.py
# Estos artefactos se generan/obtienen fuera de Git y deben copiarse localmente
# a prototype-local/ antes de construir la imagen.
COPY prototype-local/modelo.joblib /app/modelo.joblib
COPY prototype-local/ShopFast_datos.zip /app/ShopFast_datos.zip

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
