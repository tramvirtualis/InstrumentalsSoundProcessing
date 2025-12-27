# Advanced Voice Analysis Features

## Tổng quan

Module **Advanced Voice Analysis** áp dụng các kỹ thuật xử lý tiếng nói cho phân tích âm thanh nhạc cụ. Các kỹ thuật này bao gồm:

## Các tính năng

### 1. **LPC Analysis (Linear Predictive Coding)**
- **Mô tả**: Phân tích hệ số dự báo tuyến tính để mô hình hóa đặc tính phổ của nhạc cụ
- **Ứng dụng**: 
  - Nén âm thanh
  - Nhận dạng nhạc cụ
  - Phân tích timbre
- **Output**:
  - LPC coefficients (order 12)
  - Cepstral coefficients
  - Autocorrelation plot

### 2. **Waveform Visualization**
- **Mô tả**: Hiển thị dạng sóng chi tiết của âm thanh
- **Tính năng**:
  - Vẽ waveform trên canvas với 600 điểm
  - Hiển thị thông tin sample rate, độ dài
  - Tương tác real-time

### 3. **Formant Analysis**
- **Mô tả**: Phân tích các đỉnh phổ (formants) đặc trưng của nhạc cụ
- **Ứng dụng**:
  - Nhận dạng đặc tính âm sắc (timbre)
  - Phân biệt các loại nhạc cụ
  - Phân tích cấu trúc hài
- **Output**: Danh sách các formants với tần số và độ lớn

### 4. **Pitch Tracking**
- **Mô tả**: Theo dõi cao độ (pitch) của nhạc cụ theo thời gian
- **Thuật toán**: pYIN (probabilistic YIN)
- **Tính năng**:
  - Vẽ đồ thị pitch theo thời gian
  - Chuyển đổi tần số sang note name
  - Phát hiện vibrato và pitch bend

### 5. **Detailed Spectrogram**
- **Mô tả**: Spectrogram chi tiết sử dụng FFT 512-point
- **Tính năng**:
  - Pre-emphasis filter
  - Hamming window
  - Hiển thị chi tiết cấu trúc tần số-thời gian

## Cách sử dụng

1. **Upload file âm thanh** từ Dashboard
2. Chuyển đến tab **"Advanced Voice Analysis"** trong menu
3. Chọn loại phân tích muốn thực hiện:
   - Click **LPC Analysis** để phân tích hệ số LPC
   - Click **Waveform** để xem dạng sóng
   - Click **Formants** để phân tích formants
   - Click **Pitch Tracking** để theo dõi cao độ
   - Click **Detailed Spectrogram** để xem spectrogram chi tiết

## Kỹ thuật áp dụng

### Pre-emphasis Filter
```python
y[n] = x[n] - α * x[n-1]  # α = 0.9
```

### Hamming Window
```python
w[n] = 0.54 - 0.46 * cos(2πn/N)
```

### Autocorrelation
Sử dụng `librosa.autocorrelate()` để tính tự tương quan

### LPC Coefficients
Sử dụng `librosa.lpc()` với order = 12

### Cepstral Coefficients
Chuyển đổi từ LPC coefficients theo công thức:
```
c[m] = a[m] + Σ(k/m * c[k] * a[m-k])
```

## API Endpoints

### POST `/analyze/lpc`
Phân tích LPC
```json
{
  "filename": "audio.wav"
}
```

### POST `/analyze/waveform`
Tạo dữ liệu waveform
```json
{
  "filename": "audio.wav"
}
```

### POST `/analyze/formants`
Phân tích formants
```json
{
  "filename": "audio.wav"
}
```

### POST `/analyze/pitch`
Theo dõi pitch
```json
{
  "filename": "audio.wav"
}
```

### POST `/analyze/detailed_spectrogram`
Tạo spectrogram chi tiết
```json
{
  "filename": "audio.wav"
}
```

## Tham khảo

Các kỹ thuật này được chuyển đổi từ code xử lý tiếng nói trong thư mục `Xử lý tiếng nói/`:
- `my_lpc.py` - LPC analysis
- `my_speech_recording.py` - Waveform visualization
- `spectrogram.py` - Detailed spectrogram
- `my_fourier.py` - FFT analysis

## Yêu cầu

- Python 3.8+
- librosa
- scipy
- numpy
- soundfile
- matplotlib
