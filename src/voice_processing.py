import numpy as np
import librosa
import soundfile as sf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import io
import base64

class InstrumentVoiceProcessor:
    """
    Xử lý âm thanh nhạc cụ sử dụng kỹ thuật DSP từ xử lý tiếng nói
    Đã tối ưu hóa các tham số cho nhạc cụ thay vì giọng nói
    
    Khác biệt chính với speech processing:
    - Sample rate cao hơn (22050Hz vs 16000Hz) để capture harmonics
    - Frame length dài hơn để phân tích tần số thấp
    - LPC order cao hơn cho cấu trúc phức tạp của nhạc cụ
    """
    
    def __init__(self, sample_rate=22050):
        """
        Args:
            sample_rate: Tần số lấy mẫu (mặc định 22050Hz cho nhạc cụ)
                        Speech thường dùng 16000Hz
                        Music thường dùng 22050Hz hoặc 44100Hz
        """
        self.sample_rate = sample_rate
        
    def extract_frame(self, audio_path, start_index=50, frame_length=1024):
        """
        Trích xuất một frame từ file âm thanh
        Tối ưu hóa đặc biệt cho MP3: dùng librosa để load và tự động bỏ qua khoảng lặng
        """
        print(f"DEBUG extract_frame: Loading {audio_path} via librosa...")
        
        # Dùng librosa.load để hỗ trợ MP3 tốt hơn
        # sr=None để giữ sample rate gốc của file
        try:
            y, fs = librosa.load(audio_path, sr=None, mono=True)
            print(f"DEBUG extract_frame: Loaded {len(y)} samples at {fs}Hz")
        except Exception as e:
            print(f"ERROR extract_frame: Fails to load with librosa: {e}")
            # Fallback sang soundfile nếu librosa lỗi
            data, fs = sf.read(audio_path, dtype='float32')
            y = data if len(data.shape) == 1 else data[:, 0]

        total_length = len(y)
        
        # 1. Tự động "Trim" khoảng lặng ở đầu (Quan trọng cho MP3)
        # top_db=30 là ngưỡng nhạy để phát hiện âm thanh
        yt, index = librosa.effects.trim(y, top_db=30)
        start_trim = index[0]
        
        if start_trim > 0:
            print(f"DEBUG extract_frame: Skipped {start_trim} samples of silence at the beginning")
        
        # 2. Tính toán vị trí dựa trên phần âm thanh đã trim
        # Start_index (ms) cộng dồn vào vị trí sau khi đã trim silence
        offset_samples = int(start_index * (fs / 1000))
        bat_dau = start_trim + offset_samples
        ket_thuc = bat_dau + frame_length
        
        # Đảm bảo không vượt quá độ dài file
        if bat_dau >= total_length - 256:
            bat_dau = max(0, total_length - frame_length)
            ket_thuc = total_length
        elif ket_thuc > total_length:
            ket_thuc = total_length
            bat_dau = max(0, ket_thuc - frame_length)
            
        x = y[bat_dau:ket_thuc]
        
        # Kiểm tra năng lượng (RMS) lần cuối
        rms = np.sqrt(np.mean(x**2))
        print(f"DEBUG extract_frame: Final frame RMS: {rms:.6f}")
        
        if rms < 0.0001:
            # Nếu vẫn không có năng lượng, thử tìm frame mạnh nhất trong 2 giây đầu
            print("DEBUG extract_frame: Low energy, searching for strongest frame...")
            search_area = y[start_trim : start_trim + int(fs * 2)]
            if len(search_area) > frame_length:
                # Tìm frame có RMS cao nhất
                rms_frames = librosa.feature.rms(y=search_area, frame_length=frame_length, hop_length=frame_length//2)
                best_frame_idx = np.argmax(rms_frames)
                bat_dau = start_trim + (best_frame_idx * (frame_length // 2))
                x = y[bat_dau : bat_dau + frame_length]
                rms = np.sqrt(np.mean(x**2))
                print(f"DEBUG extract_frame: Found stronger frame at {bat_dau}, RMS: {rms:.6f}")

        # Chuẩn hóa nếu cần (librosa load đã chuẩn hóa về -1..1)
        return x, fs
    
    def pre_emphasis(self, signal, alpha=0.9):
        """
        Áp dụng pre-emphasis filter
        """
        N = len(signal)
        y = np.zeros((N,), np.float32)
        for n in range(N):
            if n == 0:
                y[n] = signal[n] - alpha * signal[n]
            else:
                y[n] = signal[n] - alpha * signal[n-1]
        return y
    
    def apply_hamming_window(self, signal):
        """
        Áp dụng cửa sổ Hamming
        """
        N = len(signal)
        w = np.zeros((N,), np.float32)
        for n in range(N):
            w[n] = 0.54 - 0.46 * np.cos(2 * np.pi * n / N)
        return signal * w
    
    def lpc_analysis(self, audio_path, order=20, start_index=50, frame_length=1024):
        """
        Phân tích Linear Predictive Coding cho nhạc cụ
        
        Args:
            order: LPC order (20 cho instruments vs 12 cho speech)
                   Order cao hơn để mô hình hóa cấu trúc harmonic phức tạp
            start_index: Vị trí bắt đầu (ms)
            frame_length: Độ dài frame (samples)
        
        Returns:
            dict: LPC coefficients, cepstral coefficients, autocorrelation
        """
        # Trích xuất frame
        x, fs = self.extract_frame(audio_path, start_index, frame_length)
        
        print(f"DEBUG LPC: Frame length={len(x)}, Sample rate={fs}")
        print(f"DEBUG LPC: Signal range: min={np.min(x):.6f}, max={np.max(x):.6f}")
        print(f"DEBUG LPC: Signal RMS: {np.sqrt(np.mean(x**2)):.6f}")
        
        # Check if signal has energy
        signal_energy = np.sum(x**2)
        if signal_energy < 1e-10:
            raise ValueError(f"Signal has no energy (RMS={np.sqrt(np.mean(x**2)):.6f}). File might be silent or corrupted.")
        
        # Pre-emphasis (giảm alpha cho instruments để giữ bass)
        y = self.pre_emphasis(x, alpha=0.7)  # 0.7 cho instruments vs 0.9 cho speech
        
        print(f"DEBUG LPC: After pre-emphasis: min={np.min(y):.6f}, max={np.max(y):.6f}")
        
        # Nhân với cửa sổ Hamming
        z = self.apply_hamming_window(y)
        
        print(f"DEBUG LPC: After Hamming: min={np.min(z):.6f}, max={np.max(z):.6f}")
        print(f"DEBUG LPC: Hamming RMS: {np.sqrt(np.mean(z**2)):.6f}")
        
        # Check if windowed signal has energy
        if np.sqrt(np.mean(z**2)) < 1e-10:
            raise ValueError("Signal lost all energy after windowing. This shouldn't happen.")
        
        # Tính autocorrelation
        R = librosa.autocorrelate(z, max_size=order + 1)
        print(f"DEBUG LPC: Autocorrelation R[0]={R[0]:.6f}")
        
        # Tính hệ số LPC
        try:
            a = librosa.lpc(z, order=order)
            a = -a
            print(f"DEBUG LPC: LPC coefficients computed, a[0]={a[0]:.6f}, a[1]={a[1]:.6f}")
        except Exception as e:
            print(f"ERROR LPC: Failed to compute LPC: {e}")
            raise ValueError(f"LPC computation failed: {e}")
        
        # Tính cepstral coefficients
        c = self.compute_cepstral_coefficients(a, order, max_order=30)
        
        return {
            'lpc_coefficients': a.tolist(),
            'cepstral_coefficients': c.tolist(),
            'autocorrelation': R.tolist(),
            'order': order,
            'sample_rate': int(fs),
            'frame_length': len(x),
            'signal_rms': float(np.sqrt(np.mean(x**2))),
            'analysis_type': 'Musical Instrument (optimized)'
        }
    
    def compute_cepstral_coefficients(self, a, p, max_order=18):
        """
        Tính cepstral coefficients từ hệ số LPC
        """
        c = np.zeros((max_order + 1,), dtype=np.float32)
        
        m = 1
        while m <= p:
            c[m] = a[m]
            k = 1
            while k <= m - 1:
                c[m] = c[m] + (k / m) * c[k] * a[m - k]
                k = k + 1
            m = m + 1
            
        m = p + 1
        while m <= max_order:
            c[m] = 0.0
            k = 1
            while k <= m - 1:
                chi_so = m - k
                if m - k > p:
                    temp = 0.0
                else:
                    temp = a[m - k]
                c[m] = c[m] + (k / m) * c[k] * temp
                k = k + 1
            m = m + 1
            
        return c
    
    def generate_waveform_data(self, audio_path, num_points=600):
        """
        Tạo dữ liệu waveform để hiển thị
        """
        data, fs = sf.read(audio_path, dtype='int16')
        
        # Handle mono/stereo
        if len(data.shape) > 1:
            data = data[:, 0]  # Take first channel if stereo
        
        L = len(data)
        if L < num_points:
            raise ValueError(f"Audio file too short. Need at least {num_points} samples, got {L}")
        
        N = L // num_points
        
        waveform_points = []
        for i in range(num_points - 1):
            x1 = data[i * N]
            y1 = int((int(x1) + 32768) * 300 // 65535) - 150
            waveform_points.append({
                'x': i,
                'y': y1
            })
        
        return {
            'points': waveform_points,
            'length': L,
            'sample_rate': int(fs),
            'num_segments': N
        }
    
    def generate_detailed_spectrogram(self, audio_path, output_dir, start_index=27, end_index=37):
        """
        Tạo spectrogram chi tiết với FFT (Hỗ trợ MP3 tốt hơn qua librosa)
        """
        try:
            y, fs = librosa.load(audio_path, sr=None, mono=True)
        except Exception as e:
            print(f"ERROR spectrogram: {e}")
            data, fs = sf.read(audio_path, dtype='float32')
            y = data if len(data.shape) == 1 else data[:, 0]
        
        total_length = len(y)
        
        # Tự động nhảy qua đoạn silence nếu cần
        yt, index = librosa.effects.trim(y, top_db=30)
        offset = index[0]
        
        # Adjust indices
        bat_dau = min(offset + int(start_index * (fs/1000) * 10), total_length - 1000)
        ket_thuc = min(offset + int(end_index * (fs/1000) * 10), total_length)
        
        if bat_dau < 0: bat_dau = 0
        
        data_temp = y[bat_dau:ket_thuc]
        
        if len(data_temp) < 1000:
            # Nếu đoạn lấy quá ngắn, lấy 1s từ chỗ có tiếng
            data_temp = y[offset : offset + int(fs)]
            
        L = len(data_temp)
        N = max(1, L // 600)
        
        # Tạo spectrogram matrix
        spectrogram_matrix = []
        pad_zeros = np.zeros((112,), dtype='float32')
        
        num_frames = min(600, L // N)
        for x in range(num_frames):
            a = x * N
            b = min(x * N + 400, L)
            frame = data_temp[a:b]
            
            if len(frame) < 400:
                frame = np.pad(frame, (0, 400 - len(frame)), 'constant')
            
            y_frame = np.hstack((frame, pad_zeros))
            Y = np.fft.fft(y_frame, 512)
            S = 200.0 * np.sqrt(Y.real**2 + Y.imag**2)
            S = np.clip(S, 0.001, 400)
            dark = -(S - 512) / 512 * 255
            dark = dark[:257].astype(np.int32)
            spectrogram_matrix.append(dark)
        
        # Vẽ spectrogram
        fig, ax = plt.subplots(figsize=(12, 6))
        spectrogram_array = np.array(spectrogram_matrix).T
        ax.imshow(spectrogram_array, aspect='auto', origin='lower', cmap='gray')
        ax.set_xlabel('Time Frame')
        ax.set_ylabel('Frequency Bin')
        ax.set_title('Detailed Spectrogram (MP3 Supported)')
        
        output_path = Path(output_dir) / f"detailed_spectrogram_{np.random.randint(1000, 9999)}.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path.name)
    
    def analyze_formants(self, audio_path, num_formants=8):
        """
        Phân tích harmonics/spectral peaks của nhạc cụ
        
        Lưu ý: Đối với nhạc cụ, đây thực chất là phân tích harmonics
        chứ không phải formants như trong tiếng nói.
        
        Args:
            num_formants: Số lượng harmonics cần phát hiện (8 cho instruments vs 4 cho speech)
                         Nhạc cụ có nhiều harmonics hơn giọng nói
        
        Returns:
            list: Danh sách các harmonics với frequency và magnitude
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # Tính STFT với window size lớn hơn cho frequency resolution tốt hơn
        D = librosa.stft(y, n_fft=4096)  # 4096 vs 2048 mặc định
        S = np.abs(D)
        
        # Tìm các đỉnh trong phổ
        freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)
        
        # Lấy trung bình phổ
        avg_spectrum = np.mean(S, axis=1)
        
        # Tìm peaks với threshold thấp hơn cho instruments
        from scipy.signal import find_peaks
        peaks, properties = find_peaks(
            avg_spectrum, 
            height=np.max(avg_spectrum) * 0.05,  # 0.05 vs 0.1 cho speech
            distance=5  # 5 vs 10 cho speech - cho phép peaks gần nhau hơn
        )
        
        # Lấy top harmonics
        if len(peaks) > num_formants:
            peak_heights = avg_spectrum[peaks]
            top_indices = np.argsort(peak_heights)[-num_formants:]
            harmonic_peaks = peaks[top_indices]
        else:
            harmonic_peaks = peaks
        
        harmonics = []
        for peak in sorted(harmonic_peaks):
            if peak < len(freqs):
                harmonics.append({
                    'frequency': float(freqs[peak]),
                    'magnitude': float(avg_spectrum[peak]),
                    'type': 'harmonic'  # Đánh dấu là harmonic chứ không phải formant
                })
        
        return harmonics
    
    def pitch_tracking(self, audio_path):
        """
        Theo dõi pitch (cao độ) của nhạc cụ theo thời gian
        
        Range mở rộng cho nhạc cụ:
        - Speech: C2 (65Hz) - C7 (2093Hz)
        - Instruments: A0 (27.5Hz) - C8 (4186Hz)
        """
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # Sử dụng pYIN algorithm với range mở rộng
        f0 = librosa.pyin(
            y, 
            fmin=librosa.note_to_hz('A0'),  # 27.5 Hz - lowest piano note
            fmax=librosa.note_to_hz('C8'),  # 4186 Hz - highest piano note
            sr=sr
        )
        
        # Lọc bỏ NaN values
        times = librosa.times_like(f0[0], sr=sr)
        valid_indices = ~np.isnan(f0[0])
        
        pitch_data = []
        for i, (time, freq) in enumerate(zip(times[valid_indices], f0[0][valid_indices])):
            pitch_data.append({
                'time': float(time),
                'frequency': float(freq),
                'note': librosa.hz_to_note(freq),
                'midi': int(librosa.hz_to_midi(freq))  # Thêm MIDI note number
            })
        
        return pitch_data[:100]  # Giới hạn 100 điểm để tránh quá tải
    
    def generate_autocorrelation_plot(self, audio_path, output_dir, max_lag=100):
        """
        Vẽ đồ thị autocorrelation
        """
        x, fs = self.extract_frame(audio_path)
        
        # Pre-emphasis và Hamming window
        y = self.pre_emphasis(x)
        z = self.apply_hamming_window(y)
        
        # Tính autocorrelation
        R = librosa.autocorrelate(z, max_size=max_lag)
        
        # Vẽ đồ thị
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(R, linewidth=2, color='#2196F3')
        ax.set_xlabel('Lag')
        ax.set_ylabel('Autocorrelation')
        ax.set_title('Autocorrelation Function')
        ax.grid(True, alpha=0.3)
        
        # Lưu file
        output_path = Path(output_dir) / f"autocorrelation_{np.random.randint(1000, 9999)}.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path.name)

    def analyze_vad(self, audio_path):
        """
        Phân đoạn tín hiệu (VAD - Voice/Activity Activity Detection)
        Sử dụng năng lượng để xác định các đoạn có âm thanh
        """
        # Load audio (use sr=None to get original sample rate)
        try:
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        except Exception as e:
            print(f"DEBUG VAD: Error loading file with librosa: {e}")
            # Fallback
            import soundfile as sf
            y, sr = sf.read(str(audio_path))
            if len(y.shape) > 1: y = np.mean(y, axis=1) # Mono conversion
            # Ensure float32
            y = y.astype(np.float32)

        if len(y) == 0:
            raise ValueError("Tệp âm thanh không có dữ liệu (Empty audio)")

        # Sử dụng librosa.effects.split để tìm các đoạn có âm thanh
        # Giảm top_db xuống 25 để nhạy hơn một chút nếu người dùng gặp lỗi không tìm thấy đoạn nào
        intervals = librosa.effects.split(y, top_db=25)
        
        segments = []
        for start, end in intervals:
            segments.append({
                "start": float(start / sr),
                "end": float(end / sr),
                "duration": float((end - start) / sr)
            })
            
        return {
            "total_segments": len(segments),
            "segments": segments,
            "total_duration": float(len(y) / sr)
        }

    def analyze_cutoff(self, audio_path):
        """
        Xác định tần số cắt (Cutoff Frequency) của tín hiệu
        Sử dụng Spectral Rolloff (tần số mà 85% năng lượng nằm dưới)
        """
        # Load audio
        try:
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        except Exception as e:
            import soundfile as sf
            y, sr = sf.read(str(audio_path))
            if len(y.shape) > 1: y = np.mean(y, axis=1)
            y = y.astype(np.float32)

        if len(y) == 0:
            return {"average_cutoff": 0, "max_cutoff": 0, "unit": "Hz", "warning": "No signal detected"}

        # Spectral Rolloff
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)[0]
        
        if len(rolloff) == 0:
            return {"average_cutoff": 0, "max_cutoff": 0, "unit": "Hz", "warning": "Could not calculate rolloff"}

        avg_cutoff = np.mean(rolloff)
        max_cutoff = np.max(rolloff)
        
        return {
            "average_cutoff": float(avg_cutoff),
            "max_cutoff": float(max_cutoff),
            "unit": "Hz"
        }

    def extract_acoustic_features(self, audio_path):
        """
        Extract Audio Features based on user request (Chapter 4 ref)
        4.1 Short-time energy
        4.2 Zero-crossing rate
        4.3 Endpoint detection
        4.5 Formant tracking
        4.6 Pitch extraction (Autocorrelation)
        4.7 Phonetic analysis (MFCCs)
        """
        # Load audio
        try:
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
        except Exception:
            import soundfile as sf
            y, sr = sf.read(str(audio_path))
            if len(y.shape) > 1: y = np.mean(y, axis=1)
            y = y.astype(np.float32)

        if len(y) == 0:
            raise ValueError("Empty audio file")

        # Configurations
        frame_length = 1024
        hop_length = 512

        # 4.1 Short-time Energy
        energy = np.array([
            np.sum(np.abs(y[i:i+frame_length]**2))
            for i in range(0, len(y), hop_length)
        ])
        ste_mean = float(np.mean(energy))

        # 4.2 Zero-crossing rate
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)
        zcr_mean = float(np.mean(zcr))

        # 4.3 Endpoint detection (Active Duration)
        intervals = librosa.effects.split(y, top_db=25)
        active_duration = float(np.sum([end-start for start, end in intervals]) / sr) if len(intervals) > 0 else 0.0
        
        # 4.6 Pitch extraction (Autocorrelation method - YIN)
        # YIN is improved autocorrelation
        f0 = librosa.yin(y, fmin=50, fmax=2000, sr=sr)
        pitch_mean = float(np.mean(f0[~np.isnan(f0)])) if np.any(~np.isnan(f0)) else 0.0

        # 4.5 Formant tracking (Simplified LPC estimate on central frame)
        # Find a strong central frame
        center_idx = len(y) // 2
        frame = y[center_idx:center_idx+frame_length]
        # LPC
        try:
            a = librosa.lpc(frame, order=12)
            roots = np.roots(a)
            roots = [r for r in roots if np.imag(r) >= 0]
            angz = np.arctan2(np.imag(roots), np.real(roots))
            freqs = sorted(angz * (sr / (2 * np.pi)))
            # Filter low freqs and too close ones
            formants = [f for f in freqs if f > 90 and f < 4000]
            f1 = formants[0] if len(formants) > 0 else 0
            f2 = formants[1] if len(formants) > 1 else 0
        except:
            f1, f2 = 0, 0

        # 4.7 Phonetic/Timbre Analysis (MFCCs)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1).tolist()

        return {
            "ste": {
                "val": ste_mean,
                "label": "Short-time Energy"
            },
            "zcr": {
                "val": zcr_mean,
                "label": "Zero-crossing Rate"
            },
            "endpoint": {
                "val": active_duration,
                "label": "Active Duration (Endpoint)"
            },
            "pitch": {
                "val": pitch_mean,
                "label": "Pitch (Autocorrelation)"
            },
            "formants": {
                "f1": float(f1),
                "f2": float(f2),
                "label": "Formants (F1, F2)"
            },
            "phonetic": {
                "mfcc": mfcc_mean[:4], # First 4 coeffs
                "label": "Phonetic Features (MFCC)"
            }
        }
