import json
import os
import pika
import redis

almacen = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)
almacen.ping()
print("Redis conectado correctamente")

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
canal.basic_qos(prefetch_count=1)


def procesar_evento(ch, method, properties, body):
    evento = json.loads(body)
    clave = f"evento:{evento['source']}:{evento['event_id']}"
    try:
        guardado = almacen.set(
            clave, json.dumps(evento), nx=True
        )
        if guardado:
            print("Evento almacenado correctamente:")
            print(json.dumps(evento, indent=4))
        else:
            print("Evento duplicado detectado:", clave)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Evento confirmado (ACK)", flush=True)
    except redis.RedisError as error:
        print("Error de persistencia:", error)
        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True,
        )
        ch.stop_consuming()


canal.basic_consume(
    queue="shopfast.events",
    on_message_callback=procesar_evento,
    auto_ack=False,
)
print("Consumidor ShopFast iniciado")
print("Esperando eventos...")
canal.start_consuming()
