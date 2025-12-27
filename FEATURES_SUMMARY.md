# 🎵 Advanced Voice Analysis - Tóm tắt nhanh

## ✨ Tính năng mới đã thêm

Đã tích hợp **5 tính năng phân tích âm thanh** sử dụng kỹ thuật xử lý tiếng nói:

### 1. 📊 LPC Analysis
**Linear Predictive Coding** - Mô hình hóa đặc tính phổ của nhạc cụ
- Hệ số LPC (order 12)
- Cepstral coefficients
- Autocorrelation plot

### 2. 🌊 Waveform Visualization
Hiển thị dạng sóng chi tiết trên canvas
- 600 điểm dữ liệu
- Real-time rendering
- Thông tin sample rate & length

### 3. 🏔️ Formant Analysis
Phân tích các đỉnh phổ (formants) đặc trưng
- Nhận dạng timbre
- Tần số và magnitude
- Spectral peaks

### 4. 🎼 Pitch Tracking
Theo dõi cao độ theo thời gian
- pYIN algorithm
- Note name conversion
- Pitch curve visualization

### 5. 🖼️ Detailed Spectrogram
Spectrogram chi tiết với FFT
- 512-point FFT
- Hamming window
- Time-frequency structure

## 🚀 Cách sử dụng nhanh

```bash
# 1. Cài đặt
pip install -r requirements.txt

# 2. Chạy server
python main.py

# 3. Mở browser
http://127.0.0.1:8000

# 4. Upload file → Chọn "Advanced Voice Analysis" → Click phân tích!
```

## 📁 Files quan trọng

| File | Mô tả |
|------|-------|
| `src/voice_processing.py` | ⭐ Module chính |
| `QUICK_START.md` | 📖 Hướng dẫn chi tiết |
| `VOICE_ANALYSIS.md` | 📚 Tài liệu kỹ thuật |
| `ARCHITECTURE.md` | 🏗️ Kiến trúc hệ thống |
| `test_voice_processing.py` | 🧪 Test script |

## 🎯 Use Cases

### Phân tích Guitar
```
Upload guitar.wav
→ Pitch Tracking (xem melody)
→ Formants (phân tích timbre)
→ LPC (đặc tính phổ)
```

### Phân tích Piano
```
Upload piano.wav
→ Detailed Spectrogram (xem harmonics)
→ Formants (overtones)
→ Waveform (attack/decay)
```

### Phân tích Vocals
```
Upload vocals.wav
→ Pitch Tracking (vocal range)
→ Formants (vowel characteristics)
→ LPC (vocal tract model)
```

## 🔧 API Endpoints mới

```
POST /analyze/lpc                    - LPC analysis
POST /analyze/waveform               - Waveform data
POST /analyze/formants               - Formant analysis
POST /analyze/pitch                  - Pitch tracking
POST /analyze/detailed_spectrogram   - Detailed spectrogram
```

## 📊 Kỹ thuật áp dụng

```
Xử lý tiếng nói/my_lpc.py              → LPC Analysis
Xử lý tiếng nói/my_speech_recording.py → Waveform
Xử lý tiếng nói/spectrogram.py         → Detailed Spectrogram
+ Thêm Formant & Pitch Tracking mới
```

## 💡 Highlights

✅ **5 loại phân tích** khác nhau  
✅ **Canvas rendering** cho waveform & pitch  
✅ **Real-time visualization**  
✅ **Modern UI/UX** với gradients & animations  
✅ **Comprehensive documentation**  
✅ **Test script** included  

## 🎨 UI Preview

```
┌─────────────────────────────────────────┐
│  Advanced Voice Analysis                │
├─────────────────────────────────────────┤
│  [LPC] [Waveform] [Formants] [Pitch]   │
│  [Detailed Spectrogram]                 │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Analysis Results Display Here     │ │
│  │  - Canvas visualizations           │ │
│  │  - Coefficient displays            │ │
│  │  - Formant lists                   │ │
│  │  - Generated plots                 │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🔗 Liên kết nhanh

- **Quick Start**: `QUICK_START.md`
- **Full Documentation**: `VOICE_ANALYSIS.md`
- **Architecture**: `ARCHITECTURE.md`
- **Integration Summary**: `INTEGRATION_SUMMARY.md`

## ⚡ Next Steps

1. ✅ Đọc `QUICK_START.md`
2. ✅ Chạy `python main.py`
3. ✅ Upload file test
4. ✅ Thử tất cả 5 tính năng
5. ✅ Xem `VOICE_ANALYSIS.md` để hiểu sâu hơn

---

**Enjoy analyzing! 🎵🎸🎹🎤**
