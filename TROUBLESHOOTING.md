# Troubleshooting Guide - Advanced Voice Analysis

## Common Issues & Solutions

### 1. ❌ "LPC Analysis Error: Cannot read properties of undefined"

**Nguyên nhân**: Server trả về lỗi thay vì dữ liệu

**Giải pháp**:
1. Kiểm tra browser console (F12) để xem error message chi tiết
2. Kiểm tra server logs trong terminal
3. Đảm bảo file đã được upload thành công
4. Refresh trang và thử lại

### 2. ❌ "Audio file too short"

**Nguyên nhân**: File âm thanh quá ngắn để phân tích

**Giải pháp**:
- LPC Analysis: Cần ít nhất 100 samples (~0.006 giây ở 16kHz)
- Waveform: Cần ít nhất 600 samples (~0.04 giây)
- Detailed Spectrogram: Cần ít nhất 1000 samples (~0.06 giây)

**Khuyến nghị**: Sử dụng file âm thanh dài ít nhất 1 giây

### 3. ❌ "File not found" hoặc "Filename is required"

**Nguyên nhân**: File chưa được upload hoặc session bị mất

**Giải pháp**:
1. Click "Reset & New File" ở session bar
2. Upload lại file
3. Thử phân tích lại

### 4. ❌ Pitch Tracking trả về ít hoặc không có data points

**Nguyên nhân**: 
- File không có pitch rõ ràng (ví dụ: drums, noise)
- Pitch nằm ngoài range C2-C7

**Giải pháp**:
- Sử dụng file có melodic content (vocals, guitar, piano)
- Đảm bảo file có chất lượng tốt, ít noise

### 5. ❌ Formants trả về rỗng

**Nguyên nhân**: Không tìm thấy spectral peaks rõ ràng

**Giải pháp**:
- Sử dụng file có harmonic content
- Tăng volume của file
- Thử với file khác

### 6. ❌ Canvas không hiển thị waveform/pitch

**Nguyên nhân**: JavaScript rendering error

**Giải pháp**:
1. Kiểm tra browser console (F12)
2. Refresh trang
3. Thử browser khác (Chrome, Firefox)
4. Clear browser cache

### 7. ❌ "Processing..." không kết thúc

**Nguyên nhân**: 
- Server đang xử lý file lớn
- Server bị crash
- Network timeout

**Giải pháp**:
1. Đợi thêm 30 giây
2. Kiểm tra server logs
3. Refresh trang
4. Restart server:
   ```bash
   # Stop server (Ctrl+C)
   python main.py
   ```

### 8. ❌ Autocorrelation/Spectrogram image không load

**Nguyên nhân**: 
- File chưa được tạo
- Path không đúng
- Permission issues

**Giải pháp**:
1. Kiểm tra thư mục `static/spectrograms/`
2. Đảm bảo thư mục có write permission
3. Kiểm tra server logs

### 9. ❌ "Module not found" errors

**Nguyên nhân**: Dependencies chưa được cài đặt

**Giải pháp**:
```bash
pip install -r requirements.txt
```

Đảm bảo tất cả packages được cài:
- fastapi
- uvicorn
- librosa
- scipy
- numpy
- soundfile
- matplotlib
- static-ffmpeg

### 10. ❌ Stereo audio issues

**Nguyên nhân**: Code cũ không handle stereo

**Giải pháp**: 
✅ Đã fix! Code hiện tại tự động convert stereo → mono

## Best Practices

### ✅ File Format
- **Khuyến nghị**: WAV, 16-bit, 16kHz-44.1kHz
- **Tránh**: MP3 với bitrate thấp, file bị nén nhiều

### ✅ File Length
- **Minimum**: 1 giây
- **Optimal**: 3-10 giây
- **Maximum**: Không giới hạn (nhưng xử lý sẽ lâu hơn)

### ✅ Content Type
- **LPC Analysis**: Bất kỳ audio nào
- **Waveform**: Bất kỳ audio nào
- **Formants**: Harmonic instruments (guitar, piano, vocals)
- **Pitch Tracking**: Melodic content (vocals, lead guitar, piano melody)
- **Detailed Spectrogram**: Bất kỳ audio nào

### ✅ Workflow
1. Upload file
2. Chạy Waveform trước để xem tổng quan
3. Chạy các phân tích khác tùy nhu cầu
4. So sánh kết quả

## Debug Mode

Để debug chi tiết:

1. **Mở Browser Console** (F12)
2. **Xem Network Tab** để theo dõi API requests
3. **Xem Console Tab** để xem JavaScript errors
4. **Xem Server Logs** trong terminal

### Server Logs Example
```
INFO:     127.0.0.1:xxxxx - "POST /analyze/lpc HTTP/1.1" 200 OK
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  ...
```

## Testing

Để test module trực tiếp:

```bash
python test_voice_processing.py
```

Đảm bảo có file `uploads/test.wav` trước khi chạy.

## Performance Tips

### 🚀 Tăng tốc độ xử lý
1. Sử dụng file ngắn hơn (3-5 giây)
2. Giảm sample rate xuống 16kHz
3. Convert sang mono trước khi upload

### 💾 Giảm memory usage
1. Xóa file cũ trong `uploads/`
2. Xóa plots cũ trong `static/spectrograms/`
3. Restart server định kỳ

## Contact & Support

Nếu vẫn gặp vấn đề:
1. Kiểm tra `INTEGRATION_SUMMARY.md`
2. Đọc `VOICE_ANALYSIS.md`
3. Xem `ARCHITECTURE.md`
4. Check GitHub issues (nếu có)

## Version Info

- Python: 3.8+
- FastAPI: Latest
- Librosa: Latest
- Browser: Chrome 90+, Firefox 88+, Edge 90+

---

**Last Updated**: 2025-12-27
