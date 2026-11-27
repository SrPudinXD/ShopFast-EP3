import json
import os
import pika
from datetime import datetime, timezone

credenciales = pika.PlainCredentials(
    os.getenv("RABBITMQ_USER", "shopfast"),
    os.environ["RABBITMQ_PASSWORD"],
)
conexion = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "127.0.0.1"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=credenciales,
    )
)
canal = conexion.channel()
canal.queue_declare(queue="shopfast.events", durable=True)
canal.confirm_delivery()

evento = {
    "event_id": "e19",
    "source": "web",
    "type": "click",
    "subject_ref": "U7",
    "product_id": "P17",
    "occurred_at": datetime.now(timezone.utc).isoformat(),
    "schema_version": 1,
    "recommendation_id": "rec-e19-prueba",
}
canal.basic_publish(
    exchange="",
    routing_key="shopfast.events",
    body=json.dumps(evento),
    mandatory=True,
    properties=pika.BasicProperties(
        delivery_mode=2,
        content_type="application/json",
    ),
)
print("Evento de prueba confirmado por RabbitMQ:")
print(json.dumps(evento, indent=4))
conexion.close()
