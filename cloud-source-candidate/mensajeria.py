import json
import os
import pika


def publicar_evento(evento):
    credenciales = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "shopfast"),
        os.environ["RABBITMQ_PASSWORD"],
    )
    conexion = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "127.0.0.1"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            credentials=credenciales,
            socket_timeout=5,
            blocked_connection_timeout=5,
        )
    )
    try:
        canal = conexion.channel()
        canal.queue_declare(queue="shopfast.events", durable=True)
        canal.confirm_delivery()
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
        return True
    finally:
        conexion.close()
