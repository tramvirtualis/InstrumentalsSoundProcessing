# Tích hợp Xử lý Tiếng Nói vào Instrumental Sound Processing

## Tóm tắt

Đã tích hợp thành công các kỹ thuật xử lý tiếng nói từ thư mục `Xử lý tiếng nói/` vào project **Instrumental Sound Processing**, áp dụng cho phân tích âm thanh nhạc cụ.

## Các file đã tạo/sửa đổi

### 1. Files mới được tạo

#### `src/voice_processing.py` ⭐
Module chính chứa class `InstrumentVoiceProcessor` với các phương thức:
- `lpc_analysis()` - Phân tích Linear Predictive Coding
- `generate_waveform_data()` - Tạo dữ liệu waveform
- `analyze_formants()` - Phân tích formants
- `pitch_tracking()` - Theo dõi pitch
- `generate_autocorrelation_plot()` - Vẽ đồ thị autocorrelation
- `generate_detailed_spectrogram()` - Tạo spectrogram chi tiết

#### `VOICE_ANALYSIS.md`
Tài liệu chi tiết về tính năng Advanced Voice Analysis

#### `test_voice_processing.py`
Script test để kiểm tra các tính năng

### 2. Files đã cập nhật

#### `main.py`
- Import module `InstrumentVoiceProcessor`
- Thêm 5 API endpoints mới:
  - `POST /analyze/lpc` - LPC analysis
  - `POST /analyze/waveform` - Waveform data
  - `POST /analyze/formants` - Formant analysis
  - `POST /analyze/pitch` - Pitch tracking
  - `POST /analyze/detailed_spectrogram` - Detailed spectrogram

#### `templates/index.html`
- Thêm menu item "Advanced Voice Analysis" trong sidebar
- Thêm view section mới `view-voice` với:
  - 5 nút phân tích (LPC, Waveform, Formants, Pitch, Detailed Spec)
  - Containers để hiển thị kết quả
  - Canvas elements cho waveform và pitch visualization
- Thêm JavaScript handlers cho tất cả các tính năng
- Canvas rendering cho waveform và pitch tracking

#### `static/style.css`
- Thêm CSS cho `.analysis-card`
- Thêm styles cho `.btn-primary` và `.btn-secondary`
- Styling cho voice analysis components

#### `requirements.txt`
- Thêm `soundfile`
- Thêm `static-ffmpeg`

#### `README.md`
- Cập nhật danh sách tính năng
- Cập nhật cấu trúc thư mục

## Kỹ thuật đã áp dụng

### 1. LPC Analysis (từ `my_lpc.py`)
- Pre-emphasis filter với α = 0.9
- Hamming window
- Autocorrelation với librosa
- Tính LPC coefficients (order 12)
- Chuyển đổi sang cepstral coefficients

### 2. Waveform Visualization (từ `my_speech_recording.py`)
- Downsampling để hiển thị 600 điểm
- Normalization và scaling
- Canvas rendering với HTML5 Canvas API

### 3. Spectrogram (từ `spectrogram.py`)
- FFT 512-point
- Hamming window
- Frame-by-frame processing
- Grayscale visualization

### 4. Formant Analysis (mới)
- STFT với librosa
- Peak detection trong phổ tần số
- Identification của spectral peaks

### 5. Pitch Tracking (mới)
- pYIN algorithm từ librosa
- Frequency to note conversion
- Time-series visualization

## Luồng hoạt động

```
User uploads file
    ↓
Chọn "Advanced Voice Analysis" từ menu
    ↓
Chọn loại phân tích:
    ├─ LPC Analysis → Hiển thị coefficients + autocorrelation plot
    ├─ Waveform → Vẽ waveform trên canvas
    ├─ Formants → Hiển thị danh sách formants
    ├─ Pitch Tracking → Vẽ pitch curve trên canvas
    └─ Detailed Spectrogram → Hiển thị spectrogram image
```

## API Response Examples

### LPC Analysis Response
```json
{
  "message": "LPC analysis complete",
  "lpc_data": {
    "lpc_coefficients": [1.0, -0.234, ...],
    "cepstral_coefficients": [0.0, -0.234, ...],
    "autocorrelation": [1.0, 0.95, ...],
    "order": 12
  },
  "autocorrelation_plot": "/static/spectrograms/autocorrelation_1234.png"
}
```

### Formant Analysis Response
```json
{
  "message": "Formant analysis complete",
  "formants": [
    {"frequency": 523.25, "magnitude": 0.85},
    {"frequency": 1046.50, "magnitude": 0.72},
    ...
  ]
}
```

## Cách sử dụng

1. **Khởi động server**:
   ```bash
   python main.py
   ```

2. **Truy cập**: `http://127.0.0.1:8000`

3. **Upload file âm thanh** từ Dashboard

4. **Chuyển đến tab "Advanced Voice Analysis"**

5. **Chọn loại phân tích muốn thực hiện**

## Testing

Chạy test script:
```bash
python test_voice_processing.py
```

Lưu ý: Cần có file `uploads/test.wav` để test

## Điểm nổi bật

✅ **Tích hợp hoàn chỉnh** - Tất cả kỹ thuật từ code xử lý tiếng nói đã được chuyển đổi

✅ **UI/UX đẹp** - Giao diện hiện đại với canvas visualization

✅ **Real-time rendering** - Waveform và pitch được vẽ trực tiếp trên canvas

✅ **Comprehensive analysis** - 5 loại phân tích khác nhau

✅ **Well documented** - Có tài liệu chi tiết và test script

## Dependencies mới

- `soundfile` - Đọc/ghi file audio
- `static-ffmpeg` - FFmpeg backend cho librosa
- `scipy` - Signal processing (đã có sẵn)

## Tương thích

- ✅ Python 3.8+
- ✅ Windows/Linux/macOS
- ✅ Modern browsers (Chrome, Firefox, Edge)
- ✅ Responsive design

## Kết luận

Đã tích hợp thành công các kỹ thuật xử lý tiếng nói vào project, tạo thành một tính năng mới "Advanced Voice Analysis" với đầy đủ chức năng phân tích âm thanh nhạc cụ sử dụng các kỹ thuật DSP tiên tiến.
