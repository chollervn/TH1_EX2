"""Mo phong sensor01 gui JSON moi 3 giay."""
import json
import random
import pika
from amqp import run


def make_payload():
    return {"device_id": "sensor01", "temperature": round(random.uniform(20, 40), 1),
            "humidity": round(random.uniform(30, 80), 1)}


def main(connection):
    channel = connection.channel()
    channel.queue_declare(queue="sensor_data_queue", durable=True)
    channel.confirm_delivery()
    while True:
        payload = json.dumps(make_payload())
        channel.basic_publish(exchange="", routing_key="sensor_data_queue", body=payload,
                              properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
                              mandatory=True)
        print(f"Da gui: {payload}", flush=True)
        connection.sleep(3)


if __name__ == "__main__":
    run(main)
