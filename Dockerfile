# Prototipo local; no es el Dockerfile original de EC2.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY prototype-local/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip && python -m pip install --no-cache-dir -r /app/requirements.txt
COPY prototype-local/api.py /app/api.py
EXPOSE 8000
CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]