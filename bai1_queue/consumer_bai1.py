"""Nhan loi chao va in thoi diem nhan."""
from datetime import datetime
from amqp import consume, run


def on_message(channel, method, properties, body):
    print(f"Da nhan message: {body.decode('utf-8', errors='replace')}")
    print(f"Thoi gian nhan: {datetime.now():%H:%M:%S}", flush=True)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main(connection):
    consume(connection, "iot_lab_queue", on_message)


if __name__ == "__main__":
    run(main)
