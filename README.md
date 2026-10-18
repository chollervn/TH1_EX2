# Thực hành Python AMQP

Ba bài thực hành dùng Python 3.9+ và Pika, kết nối RabbitMQ qua AMQP 0-9-1.

| Thư mục | Nội dung |
| --- | --- |
| `bai1_queue` | Gửi lời chào và nhận message kèm thời điểm nhận |
| `bai2_sensor` | Gửi JSON cảm biến mỗi 3 giây và giám sát ngưỡng |
| `bai3_alert` | Phân phối warning/critical bằng direct exchange |

Mỗi thư mục có `amqp.py` hỗ trợ kết nối, xác nhận message và đóng kết nối khi Ctrl+C. Có thể chạy các lệnh dưới đây từ thư mục gốc repo.

## Chuẩn bị

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Broker mặc định: RabbitMQ tại `localhost:5672`, virtual host `/`, tài khoản `guest/guest`. Có thể dùng RabbitMQ đã cài sẵn. Hoặc mở Docker Desktop, chờ Docker chạy rồi tạo broker thực hành:

```powershell
docker run -d --name th1-ex2-rabbitmq -p 127.0.0.1:5672:5672 -p 127.0.0.1:15672:15672 rabbitmq:4-management
docker logs th1-ex2-rabbitmq
```

Chờ log báo broker khởi động xong. Trang quản trị: http://localhost:15672 (`guest/guest`). Khi container đã tồn tại, dùng `docker start th1-ex2-rabbitmq`.

Nếu dùng broker của lớp, đặt các biến trong **từng terminal** trước khi chạy:

```powershell
$env:AMQP_HOST = "dia-chi-broker"
$env:AMQP_PORT = "5672"
$env:AMQP_USER = "tai-khoan"
$env:AMQP_PASSWORD = "mat-khau"
$env:AMQP_VHOST = "/"
```

Không đặt các biến trên nếu dùng cấu hình mặc định. Tài khoản guest chỉ dùng cho broker local. Chương trình dùng AMQP TCP; broker bắt buộc TLS cần bổ sung cấu hình TLS trước khi sử dụng.

## Bài 1 — Queue

Terminal 1:

```powershell
python bai1_queue/consumer_bai1.py
```

Terminal 2 (thay thông tin mẫu bằng thông tin của bạn):

```powershell
python bai1_queue/producer_bai1.py --name "Nguyen Van A" --student-id "B21xxxx"
```

Producer gửi một lời chào vào `iot_lab_queue`. Có thể chạy lại để gửi thêm. Kết quả mong đợi ở consumer:

```text
Da nhan message: Xin chao tu ung dung Python AMQP - B21xxxx - Nguyen Van A
Thoi gian nhan: 14:05:21
```

## Bài 2 — Sensor

Terminal 1:

```powershell
python bai2_sensor/monitor_consumer_bai2.py
```

Terminal 2:

```powershell
python bai2_sensor/sensor_producer_bai2.py
```

Producer sinh ngẫu nhiên nhiệt độ 20–40°C và độ ẩm 30–80%, làm tròn một chữ số thập phân; gửi ngay rồi lặp mỗi 3 giây vào `sensor_data_queue`. Payload:

```json
{"device_id": "sensor01", "temperature": 36.4, "humidity": 38.9}
```

Kết quả mong đợi cho payload trên:

```text
Device: sensor01
Temperature: 36.4
Humidity: 38.9
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
```

Hai ngưỡng kiểm tra độc lập: nhiệt độ **>35**, độ ẩm **<40**. Đúng 35 và 40 không cảnh báo. Giá trị ngẫu nhiên nên không phải bản tin nào cũng có cảnh báo. Payload sai JSON, thiếu trường hoặc sai kiểu bị loại bỏ có thông báo; consumer tiếp tục nhận.

## Bài 3 — Alert

Chạy hai consumer trước và chờ cả hai in `Dang cho tai ...` để các binding được tạo.

Terminal 1:

```powershell
python bai3_alert/warning_consumer_bai3.py
```

Terminal 2:

```powershell
python bai3_alert/critical_consumer_bai3.py
```

Terminal 3:

```powershell
python bai3_alert/alert_producer_bai3.py
```

Producer gửi ba mức `info`, `warning`, `critical` vào direct exchange `iot_alert_exchange` với routing key tương ứng.

| Routing key | Kết quả mong đợi |
| --- | --- |
| `info` | Không consumer nào trong bài nhận |
| `warning` | Chỉ `warning_queue` nhận |
| `critical` | Chỉ `critical_queue` nhận |

```text
[warning_queue] Da nhan: Nhiet do phong may vuot nguong warning
[critical_queue] Da nhan: Cam bien kho lanh mat ket noi critical
```

`info` bị broker bỏ qua vì không có binding phù hợp. Nếu chạy producer trước khi có binding ở lần đầu, warning/critical cũng chưa có nơi nhận.

## Dừng và xử lý lỗi

Nhấn `Ctrl+C` trong từng terminal. Consumer chạy liên tục, xác nhận sau khi xử lý; queue và exchange dùng `durable=True`, message dùng persistent delivery. Bản tin chờ có thể còn trong queue giữa các lần chạy. Có thể xóa bản tin thử bằng nút Purge trên trang quản trị RabbitMQ đúng queue cần dọn.

Nếu lỗi kết nối, kiểm tra RabbitMQ đã chạy, cổng 5672 và các biến môi trường. Sau khi sửa, chạy lại chương trình; không tự phục hồi kết nối trong lúc đang chạy. Nếu báo `PRECONDITION_FAILED`, queue/exchange cùng tên có thể đã được tạo với thuộc tính khác; dùng broker/vhost thực hành riêng hoặc xóa đúng đối tượng thực hành đó rồi chạy lại.

## Kiểm tra

```powershell
python -m unittest discover -s bai2_sensor -p "test_*.py" -v
python -m compileall -q bai1_queue bai2_sensor bai3_alert
```

Unit test kiểm tra dữ liệu cảm biến, ngưỡng biên, hai cảnh báo đồng thời và loại bỏ payload lỗi. Để kiểm tra truyền/nhận thật và routing, chạy ba bài theo các bước trên với RabbitMQ đang hoạt động. Các đầu ra trong README là ví dụ mong đợi.

Tham khảo: [RabbitMQ Python routing](https://www.rabbitmq.com/tutorials/tutorial-four-python).
