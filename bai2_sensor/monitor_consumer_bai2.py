"""Doc telemetry va canh bao nhiet do >35, do am <40."""
import json
import math
from amqp import consume, run


def parse_payload(body):
    data = json.loads(body)
    if not isinstance(data, dict) or not isinstance(data.get("device_id"), str) or not data["device_id"].strip():
        raise ValueError("device_id phai la chuoi khong rong")
    for key in ("temperature", "humidity"):
        value = data[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{key} phai la so huu han")
    if not 0 <= data["humidity"] <= 100:
        raise ValueError("humidity phai trong 0..100")
    return data


def on_message(channel, method, properties, body):
    try:
        data = parse_payload(body)
    except (ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f"Bo qua payload loi: {exc}", flush=True)
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        return
    print(f"Device: {data['device_id']}")
    print(f"Temperature: {data['temperature']}")
    print(f"Humidity: {data['humidity']}")
    if data["temperature"] > 35:
        print("CANH BAO: Nhiet do cao")
    if data["humidity"] < 40:
        print("CANH BAO: Do am thap")
    print("--------------------", flush=True)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main(connection):
    consume(connection, "sensor_data_queue", on_message)


if __name__ == "__main__":
    run(main)
