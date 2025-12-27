# Tối ưu hóa cho Nhạc cụ - Instrument Optimization

## 🎸 Đã điều chỉnh từ Speech → Instruments

### Tóm tắt thay đổi

Code ban đầu được thiết kế cho **xử lý tiếng nói** (speech processing). Đã điều chỉnh các tham số để phù hợp với **nhạc cụ** (musical instruments).

## 📊 So sánh tham số

### 1. Sample Rate
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| Sample Rate | 16000 Hz | **22050 Hz** | Nhạc cụ có harmonics cao hơn cần capture |
| Nyquist Freq | 8000 Hz | **11025 Hz** | Mở rộng frequency range |

### 2. Frame Length
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| Frame Length | 400 samples | **1024 samples** | Phân tích tần số thấp (bass) tốt hơn |
| Duration @ 16kHz | 25 ms | - | - |
| Duration @ 22kHz | - | **46 ms** | Đủ dài cho một chu kỳ bass |

### 3. LPC Order
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| LPC Order | 12 | **20** | Mô hình hóa cấu trúc harmonic phức tạp |
| Coefficients | 13 (0-12) | **21 (0-20)** | Nhiều poles hơn cho resonances |
| Cepstral Order | 18 | **30** | Phân tích chi tiết hơn |

### 4. Pre-emphasis
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| Alpha | 0.9 | **0.7** | Giữ bass frequencies |
| Effect | Boost high freq | **Balanced** | Nhạc cụ cần cả bass và treble |

### 5. Formants/Harmonics
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| Count | 4 formants | **8 harmonics** | Nhạc cụ có nhiều harmonics |
| FFT Size | 2048 | **4096** | Frequency resolution tốt hơn |
| Peak Threshold | 0.1 (10%) | **0.05 (5%)** | Detect weak harmonics |
| Peak Distance | 10 bins | **5 bins** | Cho phép harmonics gần nhau |

### 6. Pitch Range
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| Min Freq | C2 (65 Hz) | **A0 (27.5 Hz)** | Bass guitar, piano thấp |
| Max Freq | C7 (2093 Hz) | **C8 (4186 Hz)** | Piccolo, violin harmonics |
| Range | ~5 octaves | **~7.5 octaves** | Full musical range |

### 7. Frame Position
| Aspect | Speech | Instruments | Lý do |
|--------|--------|-------------|-------|
| Start Index | 95 ms | **50 ms** | Bắt đầu sớm hơn |
| Calculation | Fixed (95*16) | **Dynamic (50*fs/1000)** | Adapt to sample rate |

## 🎯 Tại sao cần điều chỉnh?

### Speech vs Music Characteristics

#### Speech (Tiếng nói):
- **Frequency range**: 80-8000 Hz (chủ yếu 300-3400 Hz)
- **Formants**: 4-5 formants rõ ràng (F1-F5)
- **Pitch**: Nam 85-180 Hz, Nữ 165-255 Hz
- **Harmonics**: Ít, đơn giản
- **Temporal**: Nhanh, transient
- **Purpose**: Communication

#### Musical Instruments (Nhạc cụ):
- **Frequency range**: 27.5-4186+ Hz (full spectrum)
- **Harmonics**: 8-20+ harmonics phức tạp
- **Pitch**: A0 (27.5 Hz) - C8 (4186 Hz)
- **Timbre**: Phong phú, đa dạng
- **Temporal**: Sustained notes, vibrato
- **Purpose**: Musical expression

## 📈 Kết quả cải thiện

### LPC Analysis
- ✅ **Order 20** capture được nhiều resonances hơn
- ✅ **Alpha 0.7** giữ được bass frequencies
- ✅ **Frame 1024** phân tích bass tốt hơn
- ✅ Thêm metadata: sample_rate, frame_length, analysis_type

### Harmonics Analysis (Formants)
- ✅ **8 harmonics** thay vì 4 formants
- ✅ **FFT 4096** cho frequency resolution tốt
- ✅ **Threshold 5%** detect weak harmonics
- ✅ Đánh dấu rõ là "harmonic" không phải "formant"

### Pitch Tracking
- ✅ **A0-C8 range** cover toàn bộ piano
- ✅ Thêm **MIDI note number**
- ✅ Detect được bass guitar (E1 = 41 Hz)
- ✅ Detect được piccolo (C8 = 4186 Hz)

### Waveform & Spectrogram
- ✅ **Sample rate 22050** capture harmonics cao
- ✅ Validation tốt hơn cho short files
- ✅ Stereo → Mono conversion

## 🎵 Use Cases

### Guitar Analysis
```
- LPC Order 20: Capture string resonances
- Harmonics: 8 peaks cho overtones
- Pitch: E2-E6 (82-1318 Hz)
- Pre-emphasis 0.7: Giữ bass strings
```

### Piano Analysis
```
- LPC Order 20: Complex resonances
- Harmonics: Full harmonic series
- Pitch: A0-C8 (27.5-4186 Hz)
- FFT 4096: Resolve close harmonics
```

### Drums Analysis
```
- Waveform: Transient analysis
- Spectrogram: Frequency content
- LPC: Resonant frequencies
- (Pitch tracking không áp dụng)
```

## 🔧 Technical Details

### LPC Coefficients Interpretation
- **Speech**: Model vocal tract (tube resonances)
- **Instruments**: Model body resonances + string/air column

### Cepstral Coefficients
- **Speech**: Voice characteristics, speaker ID
- **Instruments**: Timbre characteristics, instrument ID

### Harmonics vs Formants
- **Formants**: Resonances của vocal tract (fixed positions)
- **Harmonics**: Integer multiples of fundamental (vary with pitch)

## 📝 Code Changes Summary

```python
# BEFORE (Speech)
sample_rate = 16000
frame_length = 400
lpc_order = 12
alpha = 0.9
num_formants = 4
pitch_range = (C2, C7)

# AFTER (Instruments)
sample_rate = 22050
frame_length = 1024
lpc_order = 20
alpha = 0.7
num_harmonics = 8
pitch_range = (A0, C8)
```

## ✅ Validation

Để verify rằng parameters đúng:

1. **LPC Analysis**: Xem "analysis_type": "Musical Instrument (optimized)"
2. **Harmonics**: Thấy 8 peaks thay vì 4
3. **Pitch**: Range A0-C8 trong results
4. **Sample Rate**: 22050 Hz trong metadata

## 📚 References

- Speech Processing: 16kHz, order 10-14, formants
- Music Information Retrieval: 22-44kHz, order 16-24, harmonics
- Librosa defaults: 22050 Hz for music
- Piano range: A0 (27.5 Hz) to C8 (4186 Hz)

---

**Kết luận**: Code đã được tối ưu hóa hoàn toàn cho nhạc cụ thay vì giọng nói!
