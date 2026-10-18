"""Gui loi chao kem ho ten va ma sinh vien."""
import pika
from amqp import run


STUDENT_ID = "B23DCCN683"
STUDENT_NAME = "Phạm Minh Quân"


def main(connection):
    channel = connection.channel()
    channel.queue_declare(queue="iot_lab_queue", durable=True)
    channel.confirm_delivery()
    message = f"Xin chao tu ung dung Python AMQP - {STUDENT_ID} - {STUDENT_NAME}"
    channel.basic_publish(exchange="", routing_key="iot_lab_queue", body=message.encode("utf-8"),
                          properties=pika.BasicProperties(delivery_mode=2, content_type="text/plain"),
                          mandatory=True)
    print(f"Da gui: {message}")


if __name__ == "__main__":
    run(main)
