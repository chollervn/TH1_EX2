"""Gui ba muc canh bao qua direct exchange."""
import pika
from amqp import run


ALERTS = {
    "info": "He thong IoT hoat dong binh thuong info",
    "warning": "Nhiet do phong may vuot nguong warning",
    "critical": "Cam bien kho lanh mat ket noi critical",
}


def main(connection):
    channel = connection.channel()
    channel.exchange_declare(exchange="iot_alert_exchange", exchange_type="direct", durable=True)
    channel.confirm_delivery()
    for level, message in ALERTS.items():
        # info khong co queue dang ky: bo qua dung theo yeu cau bai.
        channel.basic_publish(exchange="iot_alert_exchange", routing_key=level,
                              body=message.encode("utf-8"),
                              properties=pika.BasicProperties(delivery_mode=2, content_type="text/plain"))
        print(f"Da gui [{level}]: {message}")


if __name__ == "__main__":
    run(main)
