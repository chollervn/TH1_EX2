"""Ket noi RabbitMQ va xu ly dung chuong trinh."""
import os
import sys
import pika


def connect():
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=os.getenv("AMQP_HOST", "localhost"),
        port=int(os.getenv("AMQP_PORT", "5672")),
        virtual_host=os.getenv("AMQP_VHOST", "/"),
        credentials=pika.PlainCredentials(os.getenv("AMQP_USER", "guest"),
                                          os.getenv("AMQP_PASSWORD", "guest")),
        heartbeat=60, blocked_connection_timeout=30,
        connection_attempts=3, retry_delay=2, socket_timeout=5))


def run(main):
    connection = None
    try:
        connection = connect()
        main(connection)
    except KeyboardInterrupt:
        print("\nDa dung.")
    except (pika.exceptions.AMQPError, OSError, ValueError) as exc:
        print(f"Loi AMQP/cau hinh: {type(exc).__name__}. Kiem tra broker va bien AMQP_*.", file=sys.stderr)
        sys.exit(1)
    finally:
        if connection is not None and connection.is_open:
            connection.close()


def consume(connection, queue, callback):
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
    print(f"Dang cho tai {queue}. Nhan Ctrl+C de dung.", flush=True)
    channel.start_consuming()
