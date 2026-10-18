"""Gui loi chao kem ho ten va ma sinh vien."""
import argparse
import pika
from amqp import run


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Ho ten sinh vien")
    parser.add_argument("--student-id", required=True, help="Ma sinh vien")
    return parser.parse_args()


def main(connection):
    channel = connection.channel()
    channel.queue_declare(queue="iot_lab_queue", durable=True)
    channel.confirm_delivery()
    message = f"Xin chao tu ung dung Python AMQP - {args.student_id} - {args.name}"
    channel.basic_publish(exchange="", routing_key="iot_lab_queue", body=message.encode("utf-8"),
                          properties=pika.BasicProperties(delivery_mode=2, content_type="text/plain"),
                          mandatory=True)
    print(f"Da gui: {message}")


if __name__ == "__main__":
    args = parse_args()
    run(main)
