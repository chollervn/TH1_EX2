"""Kiem tra logic cam bien khong can RabbitMQ."""
import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock

from monitor_consumer_bai2 import on_message, parse_payload
from sensor_producer_bai2 import make_payload


class SensorTests(unittest.TestCase):
    def deliver(self, temperature, humidity):
        channel = Mock()
        body = json.dumps(dict(device_id="sensor01", temperature=temperature, humidity=humidity)).encode()
        output = io.StringIO()
        with redirect_stdout(output):
            on_message(channel, SimpleNamespace(delivery_tag=7), None, body)
        channel.basic_ack.assert_called_once_with(delivery_tag=7)
        channel.basic_reject.assert_not_called()
        return output.getvalue()

    def test_both_alerts(self):
        output = self.deliver(36.4, 38.9)
        self.assertIn("CANH BAO: Nhiet do cao", output)
        self.assertIn("CANH BAO: Do am thap", output)

    def test_boundaries_no_alert(self):
        self.assertNotIn("CANH BAO", self.deliver(35, 40))

    def test_independent_alerts(self):
        self.assertNotIn("Do am thap", self.deliver(36, 60))
        self.assertIn("Nhiet do cao", self.deliver(36, 60))
        self.assertNotIn("Nhiet do cao", self.deliver(25, 39))
        self.assertIn("Do am thap", self.deliver(25, 39))

    def test_invalid_messages_rejected(self):
        for body in (b"invalid", b"{}", b"[]", b"\xff",
                     b'{"device_id":"x","temperature":true,"humidity":50}',
                     b'{"device_id":"x","temperature":NaN,"humidity":50}',
                     b'{"device_id":"x","temperature":25,"humidity":101}'):
            with self.subTest(body=body), redirect_stdout(io.StringIO()):
                channel = Mock()
                on_message(channel, SimpleNamespace(delivery_tag=8), None, body)
                channel.basic_reject.assert_called_once_with(delivery_tag=8, requeue=False)
                channel.basic_ack.assert_not_called()

    def test_random_payload_schema_and_range(self):
        for _ in range(100):
            payload = make_payload()
            self.assertEqual(set(payload), {"device_id", "temperature", "humidity"})
            self.assertEqual(payload["device_id"], "sensor01")
            self.assertTrue(20 <= payload["temperature"] <= 40)
            self.assertTrue(30 <= payload["humidity"] <= 80)
            self.assertEqual(parse_payload(json.dumps(payload)), payload)


if __name__ == "__main__":
    unittest.main()
