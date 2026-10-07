# Bài 2: Mô phỏng cảm biến nhiệt độ và độ ẩm bằng MQTT

Hai chương trình Python mô phỏng thiết bị IoT gửi dữ liệu mỗi 3 giây và giám sát dữ liệu qua MQTT.

```text
publisher.py → MQTT Broker → subscriber.py
                Topic: iot/lab/sensor01/data
```

## 1. Nội dung

| File | Chức năng |
| --- | --- |
| `publisher.py` | Sinh nhiệt độ 20–40°C, độ ẩm 30–80%, làm tròn 1 chữ số thập phân và gửi JSON mỗi 3 giây |
| `subscriber.py` | Nhận JSON, in từng dòng và kiểm tra ngưỡng cảnh báo |
| `requirements.txt` | Khai báo thư viện `paho-mqtt` |
| `mosquitto.conf` | Cấu hình broker Mosquitto để chạy trên máy cá nhân |

Payload gửi đúng ba trường:

```json
{
  "device_id": "sensor01",
  "temperature": 28.5,
  "humidity": 65.2
}
```

## 2. Chuẩn bị môi trường

- Python **3.7 trở lên** (Python 3.x có hỗ trợ `paho-mqtt` 2.1.0).
- VS Code hoặc một IDE khác; có thể chạy trực tiếp bằng terminal.
- Broker MQTT, chọn một trong hai cách ở mục 3.

Mở terminal tại thư mục chứa `publisher.py` rồi cài thư viện:

```bash
python -m pip install -r requirements.txt
```

Nếu máy dùng lệnh `python3` thay cho `python`, thay tương ứng trong các lệnh dưới đây.

## 3. Cấu hình MQTT Broker

### Cách A: Chạy Mosquitto trên máy cá nhân

Cách này phù hợp để nộp bài vì topic không bị trùng với người khác trên broker công cộng.

1. Tải và cài [Eclipse Mosquitto](https://mosquitto.org/download/) theo hệ điều hành. Trên Windows, chọn bộ cài Windows x64 nếu máy dùng Windows 64-bit.
2. File `mosquitto.conf` trong bài đã cấu hình:

   ```conf
   listener 1883 127.0.0.1
   allow_anonymous true
   persistence false
   ```

   Broker chỉ nhận kết nối từ máy hiện tại ở cổng 1883, không yêu cầu tài khoản. Đây là cấu hình thực hành local.

3. Mở terminal tại thư mục bài và chạy broker, giữ terminal này mở:

   ```bash
   mosquitto -c mosquitto.conf -v
   ```

   Nếu Windows chưa có Mosquitto trong PATH, dùng PowerShell:

   ```powershell
   & "C:\Program Files\mosquitto\mosquitto.exe" -c .\mosquitto.conf -v
   ```

4. Hai chương trình mặc định dùng `localhost:1883`, nên không cần sửa code.

Nếu cổng 1883 đã bị một dịch vụ Mosquitto khác sử dụng, dùng broker đang chạy hoặc đổi dòng listener trong file thành `listener 1884 127.0.0.1`, sau đó đặt `MQTT_PORT=1884` cho cả hai chương trình.

### Cách B: Dùng broker công cộng để chạy nhanh

Có thể dùng [test.mosquitto.org](https://test.mosquitto.org/) với cổng **1883**, không yêu cầu username/password. Cách này cần Internet và không cần cài Mosquitto trên máy.

Trong **cả hai terminal**, trước khi chạy chương trình, đặt:

Windows PowerShell:

```powershell
$env:MQTT_BROKER = "test.mosquitto.org"
$env:MQTT_PORT = "1883"
```

Linux/macOS:

```bash
export MQTT_BROKER=test.mosquitto.org
export MQTT_PORT=1883
```

Broker công cộng có thể gián đoạn và người khác có thể gửi/đọc cùng topic. Chỉ dùng dữ liệu mô phỏng; để kiểm tra riêng bài của mình, dùng cách A.

### Các biến cấu hình

Hai chương trình cùng đọc các biến môi trường sau:

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `MQTT_BROKER` | `localhost` | Địa chỉ broker, chỉ nhập hostname hoặc IP, không có `mqtt://` |
| `MQTT_PORT` | `1883` | Cổng MQTT TCP |
| `MQTT_USERNAME` | Không đặt | Tên đăng nhập nếu broker yêu cầu |
| `MQTT_PASSWORD` | Không đặt | Mật khẩu nếu broker yêu cầu |

Ví dụ khi giáo viên cung cấp broker có tài khoản, đặt trong cả hai terminal PowerShell:

```powershell
$env:MQTT_BROKER = "dia-chi-broker-cua-ban"
$env:MQTT_PORT = "1883"
$env:MQTT_USERNAME = "ten-dang-nhap"
$env:MQTT_PASSWORD = "mat-khau"
```

Thay giá trị mẫu bằng thông tin thật. Chương trình sử dụng MQTT TCP, không bật TLS; cổng 8883 thường cần cấu hình TLS riêng. Để quay về broker local trong PowerShell:

```powershell
$env:MQTT_BROKER = "localhost"
$env:MQTT_PORT = "1883"
Remove-Item Env:MQTT_USERNAME, Env:MQTT_PASSWORD -ErrorAction SilentlyContinue
```

## 4. Chạy chương trình

Nếu dùng cách A, chạy broker trước. Mở hai terminal khác tại thư mục bài, cài thư viện và đặt cấu hình broker theo mục 3 nếu cần.

**Terminal 1 — chạy subscriber trước:**

```bash
python subscriber.py
```

Đợi xuất hiện `Da subscribe: iot/lab/sensor01/data. Dang cho du lieu...`.

**Terminal 2 — chạy publisher:**

```bash
python publisher.py
```

Publisher gửi ngay sau khi kết nối, sau đó gửi tiếp mỗi 3 giây. Subscriber hiển thị ví dụ:

```text
------------------------------------
Device: sensor01
Temperature: 36.1 C
Humidity: 38.7 %
CANH BAO: Nhiet do cao
CANH BAO: Do am thap
------------------------------------
```

Do dữ liệu ngẫu nhiên, kết quả mỗi lần sẽ khác nhau. Nhấn `Ctrl+C` trong từng terminal để dừng chương trình.

## 5. Nguyên tắc cảnh báo và kiểm tra

- Nhiệt độ **> 35°C**: `CANH BAO: Nhiet do cao`.
- Độ ẩm **< 40%**: `CANH BAO: Do am thap`.
- Hai điều kiện được kiểm tra bằng hai `if` độc lập, nên có thể in cả hai cảnh báo.
- Đúng 35°C hoặc 40% thì không phát cảnh báo tương ứng.
- Payload lỗi JSON, thiếu trường hoặc giá trị sai kiểu sẽ bị bỏ qua và có thông báo, subscriber tiếp tục nhận bản tin.
- Publisher dùng `json.dumps()`, subscriber dùng `json.loads()` và callback API phiên bản 2 của Paho.
- Bản tin dùng QoS 0 và `retain=False`: phù hợp dữ liệu cảm biến định kỳ; bản tin không được lưu để gửi lại cho subscriber kết nối muộn.
- Hai chương trình tự thử kết nối lại khi mất kết nối sau lần kết nối ban đầu. Nếu broker chưa chạy ở lần đầu, chương trình báo lỗi và cần chạy lại sau khi bật broker.

| Nhiệt độ (°C) | Độ ẩm (%) | Kết quả mong đợi |
| --- | --- | --- |
| 28.5 | 65.2 | Không cảnh báo |
| 36.1 | 65.2 | Nhiệt độ cao |
| 28.5 | 38.7 | Độ ẩm thấp |
| 36.1 | 38.7 | Cả hai cảnh báo |
| 35.0 | 40.0 | Không cảnh báo |

Để kiểm tra chắc chắn cảnh báo, khi subscriber đang chạy, mở một terminal thứ ba với cùng cấu hình broker. Chạy `python` để mở Python tương tác, rồi dán lần lượt:

```python
import json, os
from paho.mqtt.publish import single
data = {"device_id": "sensor01", "temperature": 36.1, "humidity": 38.7}
auth = {"username": os.environ["MQTT_USERNAME"], "password": os.getenv("MQTT_PASSWORD")} if os.getenv("MQTT_USERNAME") else None
single("iot/lab/sensor01/data", payload=json.dumps(data), hostname=os.getenv("MQTT_BROKER", "localhost"), port=int(os.getenv("MQTT_PORT", "1883")), auth=auth)
exit()
```

Dừng publisher bằng `Ctrl+C` trước khi thử dữ liệu cố định để dễ quan sát. Thay nhiệt độ và độ ẩm trong `data` để thử các dòng trong bảng.

## 6. Lỗi thường gặp

| Lỗi/hiện tượng | Cách xử lý |
| --- | --- |
| `No module named 'paho'` | Chạy `python -m pip install -r requirements.txt` bằng đúng Python đang dùng |
| Connection refused / WinError 10061 | Bật broker, kiểm tra host và port |
| Không nhận dữ liệu | Kiểm tra hai terminal cùng broker, cùng port; đợi subscriber xác nhận subscribe rồi chạy publisher |
| Broker từ chối kết nối | Kiểm tra username/password và quyền truy cập broker |
| `Address already in use` khi chạy Mosquitto | Cổng đang được dùng; dùng broker có sẵn hoặc đổi cổng ở cả broker và hai chương trình |
