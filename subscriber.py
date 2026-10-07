"""Nhan du lieu sensor01 va canh bao nhiet do cao / do am thap."""

import json
import math
import os
import sys

import paho.mqtt.client as mqtt


TOPIC = "iot/lab/sensor01/data"


def on_connect(client, state, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Broker tu choi ket noi: {reason_code}", flush=True)
        state["failed"] = True
        client.disconnect()
        return
    # Subscribe lai moi khi ket noi (ke ca sau khi mat mang).
    result, _ = client.subscribe(TOPIC, qos=0)
    if result != mqtt.MQTT_ERR_SUCCESS:
        print(f"Subscribe that bai: {mqtt.error_string(result)}", flush=True)
        state["failed"] = True
        client.disconnect()


def on_subscribe(client, state, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        print("Broker tu choi subscribe topic.", flush=True)
        state["failed"] = True
        client.disconnect()
    else:
        print(f"Da subscribe: {TOPIC}. Dang cho du lieu...", flush=True)


def parse_sensor_data(payload):
    """Kiem tra JSON va kieu du lieu truoc khi so sanh nguong."""
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Payload phai la mot JSON object")
    device_id = data["device_id"]
    temperature = data["temperature"]
    humidity = data["humidity"]
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("device_id phai la chuoi khong rong")
    for name, value in (("temperature", temperature), ("humidity", humidity)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} phai la so")
        if not math.isfinite(value):
            raise ValueError(f"{name} phai la so huu han")
    if not 0 <= humidity <= 100:
        raise ValueError("humidity phai nam trong khoang 0-100")
    return device_id, temperature, humidity


def on_message(client, userdata, message):
    try:
        device_id, temperature, humidity = parse_sensor_data(message.payload)
    except (UnicodeDecodeError, ValueError, KeyError, OverflowError) as error:
        print(f"Bo qua payload khong hop le: {error}", flush=True)
        return

    print("-" * 36)
    print(f"Device: {device_id}")
    print(f"Temperature: {temperature:.1f} C")
    print(f"Humidity: {humidity:.1f} %")
    # Hai if doc lap: co the in ca hai canh bao cung luc.
    if temperature > 35:
        print("CANH BAO: Nhiet do cao")
    if humidity < 40:
        print("CANH BAO: Do am thap")
    print("-" * 36, flush=True)


def main():
    state = {"failed": False}
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=state)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=10)

    broker = os.getenv("MQTT_BROKER", "localhost")
    username = os.getenv("MQTT_USERNAME")
    if username:
        client.username_pw_set(username, os.getenv("MQTT_PASSWORD"))

    try:
        port = int(os.getenv("MQTT_PORT", "1883"))
        if not 1 <= port <= 65535:
            raise ValueError("MQTT_PORT phai nam trong khoang 1-65535")
        print(f"Dang ket noi {broker}:{port}...", flush=True)
        client.connect(broker, port, keepalive=60)
        client.loop_forever()  # Nhan ban tin va tu ket noi lai khi mat mang.
    except KeyboardInterrupt:
        print("\nDa dung subscriber.", flush=True)
    except (OSError, ValueError) as error:
        print(f"Loi: {error}. Kiem tra broker va cau hinh MQTT.", file=sys.stderr)
        return 1
    finally:
        client.disconnect()
    return 1 if state["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
