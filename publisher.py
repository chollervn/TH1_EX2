"""Mo phong sensor01 gui nhiet do va do am qua MQTT moi 3 giay."""

import json
import os
import random
import sys
import threading
import time

import paho.mqtt.client as mqtt


TOPIC = "iot/lab/sensor01/data"
DEVICE_ID = "sensor01"
INTERVAL_SECONDS = 3


def create_sensor_data():
    """Sinh du lieu nam trong khoang co the xuat hien ca hai canh bao."""
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(20.0, 40.0), 1),
        "humidity": round(random.uniform(30.0, 80.0), 1),
    }


def on_connect(client, connected, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Broker tu choi ket noi: {reason_code}", flush=True)
    else:
        print(f"Da ket noi broker. Topic: {TOPIC}", flush=True)
    connected.set()


def main():
    connected = threading.Event()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=connected)
    client.on_connect = on_connect
    client.reconnect_delay_set(min_delay=1, max_delay=10)

    # Doc cau hinh tu bien moi truong; mac dinh dung broker tren may local.
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
        client.loop_start()  # Xu ly mang o luong rieng trong khi vong lap gui du lieu.
        if not connected.wait(timeout=10) or not client.is_connected():
            raise ConnectionError("Khong ket noi duoc broker trong 10 giay")

        while True:
            if client.is_connected():
                payload = json.dumps(create_sensor_data(), allow_nan=False)
                result = client.publish(TOPIC, payload, qos=0, retain=False)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"Da gui: {payload}", flush=True)
                else:
                    print(f"Gui that bai: {mqtt.error_string(result.rc)}", flush=True)
            else:
                print("Mat ket noi. Dang cho ket noi lai...", flush=True)
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nDa dung publisher.", flush=True)
    except (OSError, ValueError) as error:
        print(f"Loi: {error}. Kiem tra broker va cau hinh MQTT.", file=sys.stderr)
        return 1
    finally:
        client.disconnect()
        client.loop_stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
