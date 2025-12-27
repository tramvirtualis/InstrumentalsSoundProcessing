# Quick Start Guide - Advanced Voice Analysis

## Bắt đầu nhanh

### 1. Cài đặt Dependencies

```bash
# Kích hoạt virtual environment (nếu có)
.\.venv\Scripts\activate  # Windows
# hoặc
source .venv/bin/activate  # Linux/macOS

# Cài đặt packages
pip install -r requirements.txt
```

### 2. Khởi động Server

```bash
python main.py
```

Server sẽ chạy tại: `http://127.0.0.1:8000`

### 3. Sử dụng Advanced Voice Analysis

#### Bước 1: Upload File
1. Mở trình duyệt và truy cập `http://127.0.0.1:8000`
2. Click vào khu vực upload trên Dashboard
3. Chọn file âm thanh (MP3, WAV, FLAC)

#### Bước 2: Chuyển đến Voice Analysis
1. Click vào menu **"Advanced Voice Analysis"** (icon wave-square)
2. Bạn sẽ thấy 5 nút phân tích

#### Bước 3: Thực hiện phân tích

##### 🔹 LPC Analysis
- Click **"LPC Analysis"**
- Xem:
  - LPC Coefficients (12 coefficients)
  - Cepstral Coefficients
  - Autocorrelation Plot

##### 🔹 Waveform
- Click **"Waveform"**
- Xem:
  - Dạng sóng được vẽ trên canvas
  - Thông tin: Length, Sample Rate, Segments

##### 🔹 Formants
- Click **"Formants"**
- Xem:
  - Danh sách các formants (spectral peaks)
  - Tần số và magnitude của mỗi formant

##### 🔹 Pitch Tracking
- Click **"Pitch Tracking"**
- Xem:
  - Đồ thị pitch theo thời gian
  - Note names và frequencies

##### 🔹 Detailed Spectrogram
- Click **"Detailed Spectrogram"**
- Xem:
  - Spectrogram FFT-based chi tiết
  - Cấu trúc tần số-thời gian

## Ví dụ sử dụng

### Phân tích Guitar Solo
1. Upload file guitar solo
2. Chạy **Pitch Tracking** → Xem melody line
3. Chạy **Formants** → Phân tích timbre
4. Chạy **LPC Analysis** → Xem đặc tính phổ

### Phân tích Piano
1. Upload file piano
2. Chạy **Detailed Spectrogram** → Xem harmonics
3. Chạy **Formants** → Phân tích overtones
4. Chạy **Waveform** → Xem attack và decay

### Phân tích Vocals
1. Upload file vocals
2. Chạy **Pitch Tracking** → Xem vocal range
3. Chạy **Formants** → Phân tích vowel characteristics
4. Chạy **LPC Analysis** → Xem vocal tract model

## Tips & Tricks

### 💡 Tip 1: Chất lượng file
- Sử dụng file WAV không nén để có kết quả tốt nhất
- Sample rate khuyến nghị: 16kHz - 44.1kHz

### 💡 Tip 2: Kết hợp các phân tích
- Chạy nhiều loại phân tích để có cái nhìn toàn diện
- So sánh kết quả giữa các nhạc cụ khác nhau

### 💡 Tip 3: Hiểu kết quả
- **LPC Coefficients**: Mô hình hóa vocal tract/resonance
- **Formants**: Đặc trưng timbre của nhạc cụ
- **Pitch**: Cao độ và melody
- **Waveform**: Cấu trúc thời gian
- **Spectrogram**: Cấu trúc tần số-thời gian

## Troubleshooting

### ❌ Lỗi: "File not found"
- Đảm bảo đã upload file thành công
- Kiểm tra session bar ở đầu trang

### ❌ Lỗi: "Processing failed"
- File có thể bị lỗi hoặc không đúng format
- Thử với file WAV đơn giản

### ❌ Canvas không hiển thị
- Refresh trang
- Kiểm tra browser console (F12)

### ❌ Pitch tracking trống
- File có thể không có pitch rõ ràng
- Thử với file có melodic content

## API Usage (Advanced)

Nếu muốn sử dụng API trực tiếp:

```javascript
// LPC Analysis
fetch('/analyze/lpc', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ filename: 'your-file.wav' })
})
.then(res => res.json())
.then(data => console.log(data));

// Waveform
fetch('/analyze/waveform', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ filename: 'your-file.wav' })
})
.then(res => res.json())
.then(data => console.log(data));
```

## Keyboard Shortcuts

- `Ctrl + R` - Refresh page
- `F12` - Open developer console
- `Esc` - Close modals (if any)

## Next Steps

1. ✅ Thử tất cả 5 loại phân tích
2. ✅ So sánh kết quả giữa các nhạc cụ
3. ✅ Đọc `VOICE_ANALYSIS.md` để hiểu sâu hơn
4. ✅ Xem `test_voice_processing.py` để test programmatically

## Support

Nếu gặp vấn đề:
1. Kiểm tra terminal/console logs
2. Xem `INTEGRATION_SUMMARY.md`
3. Đọc `VOICE_ANALYSIS.md`
4. Check browser console (F12)

---

**Chúc bạn phân tích vui vẻ! 🎵🎸🎹**
