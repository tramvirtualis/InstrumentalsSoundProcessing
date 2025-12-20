# Instrumental Sound Processing Studio

Một ứng dụng web xử lý âm thanh chuyên dụng cho nhạc Rock/Instrumental, được xây dựng bằng **FastAPI** và **Librosa**.

## Tính năng

*   **Spectrogram Analysis**: Phân tích và hiển thị biểu đồ phổ tần số của file âm thanh.
*   **Noise Reduction**: (Mô phỏng) Khử nhiễu nền.
*   **Instrument Isolation**: Tách các nhạc cụ từ bản mix gốc sử dụng kỹ thuật xử lý tín hiệu số (DSP):
    *   **Drums**: Tách dựa trên Harmonic-Percussive Source Separation (HPSS).
    *   **Bass**: Tách bằng bộ lọc thông thấp (Low-pass Filter).
    *   **Vocals**: Tách dựa trên không gian (Center-panned).
    *   **Acoustic Guitar**: Tách phần gõ/transients nhẹ trong dải mid.
    *   **Electric Guitar**: Lọc dải tần số đặc trưng (200Hz - 4kHz).
    *   **Piano/Keys**: Phần dư còn lại của dải tần.

## Cài đặt và Chạy

### Yêu cầu
*   Python 3.8 trở lên.

### Bước 1: Tạo môi trường ảo (Virtual Environment)
```bash
python -m venv .venv
```

### Bước 2: Kích hoạt môi trường ảo
*   **Windows**:
    ```bash
    .\.venv\Scripts\activate
    ```
*   **Linux/macOS**:
    ```bash
    source .venv/bin/activate
    ```

### Bước 3: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng
```bash
uvicorn main:app --reload
```
Hoặc nếu dùng Python trực tiếp:
```bash
python main.py
```

### Bước 5: Sử dụng
Truy cập trình duyệt tại địa chỉ: `http://127.0.0.1:8000`

## Cấu trúc thư mục
*   `main.py`: Mã nguồn chính (Server FastAPI & Logic xử lý âm thanh).
*   `templates/`: Chứa file giao diện HTML.
*   `static/`: Chứa CSS và ảnh Spectrogram sinh ra.
*   `uploads/`: Nơi lưu file nhạc upload và các file đã tách (Cần tạo thư mục này nếu chưa có, code sẽ tự tạo).
