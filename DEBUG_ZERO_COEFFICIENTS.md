# Debug Guide - Zero Coefficients Issue

## 🔍 Vấn đề: Tất cả coefficients = 0.000000

Nếu bạn thấy tất cả LPC coefficients và cepstral coefficients đều bằng 0, có thể do:

### Nguyên nhân chính

1. **File âm thanh có vùng silence**
   - Frame đang được extract từ phần im lặng của file
   - Solution: File cần có âm thanh ngay từ đầu

2. **File quá ngắn**
   - Cần ít nhất 256 samples (~0.012 giây @ 22kHz)
   - Solution: Sử dụng file dài hơn 1 giây

3. **File bị corrupt hoặc không đúng format**
   - MP3 có thể có header dài
   - Solution: Convert sang WAV trước

## 🔧 Debug Steps

### Bước 1: Kiểm tra Server Logs

Sau khi click "LPC Analysis", xem terminal logs:

```
DEBUG extract_frame: Reading uploads/your-file.mp3
DEBUG extract_frame: Read XXXXX samples at XXXXXHz
DEBUG extract_frame: Raw data range: min=XXX, max=XXX
DEBUG LPC: Signal RMS: X.XXXXXX
```

### Bước 2: Phân tích Logs

#### ✅ Good Logs (File OK):
```
DEBUG extract_frame: Read 1323000 samples at 44100Hz
DEBUG extract_frame: Raw data range: min=-15234, max=18432
DEBUG LPC: Signal RMS: 0.234567
```

#### ❌ Bad Logs (File có vấn đề):
```
DEBUG extract_frame: Read 1323000 samples at 44100Hz
DEBUG extract_frame: Raw data range: min=0, max=0        ← SILENCE!
DEBUG LPC: Signal RMS: 0.000000                          ← NO SIGNAL!
```

### Bước 3: Solutions

#### Solution 1: Sử dụng file WAV
```bash
# Convert MP3 to WAV using ffmpeg
ffmpeg -i input.mp3 -ar 22050 -ac 1 output.wav
```

#### Solution 2: Trim silence từ đầu file
```bash
# Remove silence from beginning
ffmpeg -i input.mp3 -af silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB output.mp3
```

#### Solution 3: Sử dụng phần giữa file
- Thay vì extract từ đầu file (50ms)
- Extract từ giữa file (1000ms)

## 🎵 File Requirements

### Recommended Format:
- **Format**: WAV (uncompressed)
- **Sample Rate**: 22050 Hz hoặc 44100 Hz
- **Channels**: Mono (1 channel)
- **Bit Depth**: 16-bit
- **Length**: Ít nhất 1 giây
- **Content**: Có âm thanh ngay từ đầu (không bắt đầu bằng silence)

### Test Your File:
```python
import soundfile as sf
import numpy as np

# Read file
data, fs = sf.read('your-file.wav', dtype='int16')
print(f"Length: {len(data)} samples")
print(f"Sample rate: {fs} Hz")
print(f"Duration: {len(data)/fs:.2f} seconds")
print(f"Min: {np.min(data)}, Max: {np.max(data)}")
print(f"RMS: {np.sqrt(np.mean(data**2)):.2f}")

# Check first 1024 samples
first_frame = data[:1024]
print(f"First frame RMS: {np.sqrt(np.mean(first_frame**2)):.2f}")
```

## 📊 Expected Values

### Good Signal:
- **RMS**: > 100 (for int16)
- **RMS normalized**: > 0.003 (for float32 -1 to 1)
- **Min/Max**: Có variation, không phải tất cả 0

### Bad Signal (Silence):
- **RMS**: < 10 hoặc 0
- **RMS normalized**: < 0.0001
- **Min/Max**: Cả hai đều 0 hoặc rất gần 0

## 🛠️ Quick Fixes

### Fix 1: Upload file khác
- Thử với file WAV đơn giản
- Đảm bảo file có âm thanh rõ ràng

### Fix 2: Check file với audio editor
- Mở file trong Audacity
- Xem waveform
- Đảm bảo có signal ngay từ đầu

### Fix 3: Adjust start_index
Nếu file có intro dài, có thể cần adjust start position.

Hiện tại code extract từ 50ms. Nếu file có intro silence dài hơn, cần tăng lên.

## 🎯 Testing

### Test với file mẫu:
1. Download một file guitar/piano ngắn
2. Đảm bảo file bắt đầu ngay với âm thanh
3. Upload và test

### Good test files:
- Guitar strum (bắt đầu ngay với strum)
- Piano note (bắt đầu ngay với attack)
- Drum hit (bắt đầu ngay với hit)

### Bad test files:
- Files có intro silence dài
- Files có fade-in chậm
- Files quá ngắn (< 1 giây)

## 📝 Debug Checklist

- [ ] File có âm thanh ngay từ đầu?
- [ ] File dài hơn 1 giây?
- [ ] Format là WAV (không phải MP3)?
- [ ] Đã xem server logs?
- [ ] RMS > 0.003?
- [ ] Min/Max khác 0?

## 💡 Pro Tips

1. **Luôn dùng WAV** cho analysis
2. **Trim silence** trước khi upload
3. **Check waveform** trong audio editor
4. **Use mono files** (stereo sẽ tự convert nhưng mono tốt hơn)
5. **Sample rate 22050 hoặc 44100** (không quá thấp, không quá cao)

---

**Nếu vẫn gặp vấn đề**, gửi server logs để debug chi tiết hơn!
