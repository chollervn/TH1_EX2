"""Chi nhan canh bao critical."""
from amqp import consume, run


def on_message(channel, method, properties, body):
    print(f"[critical_queue] Da nhan: {body.decode('utf-8', errors='replace')}", flush=True)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main(connection):
    channel = connection.channel()
    channel.exchange_declare(exchange="iot_alert_exchange", exchange_type="direct", durable=True)
    channel.queue_declare(queue="critical_queue", durable=True)
    channel.queue_bind(exchange="iot_alert_exchange", queue="critical_queue", routing_key="critical")
    consume(connection, "critical_queue", on_message)


if __name__ == "__main__":
    run(main)
