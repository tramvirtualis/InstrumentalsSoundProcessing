import numpy as np
import librosa
import soundfile as sf
import scipy.signal
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
    
    def voice_activity_detection(self, audio_path, frame_length=2048, hop_length=512, energy_threshold=0.02, zcr_threshold=None):
        """
        Voice Activity Detection (VAD) - Endpoint Detection
        Phát hiện phần có âm thanh và phần lặng.
        
        Kết hợp hai tiêu chí:
        1. Energy (RMS) - âm thanh lớn → có voice
        2. Zero-Crossing Rate - âm thanh nhanh thay đổi → có voice
        
        Args:
            audio_path: Đường dẫn file audio
            frame_length: Độ dài frame (samples)
            hop_length: Bước nhảy giữa các frame
            energy_threshold: Ngưỡng năng lượng chuẩn hóa (0-1)
            zcr_threshold: Ngưỡng ZCR (auto nếu None)
            
        Returns:
            dict: Chứa:
                - activity_frames: List bool cho mỗi frame
                - segments: Danh sách [start_time, end_time] của voice segments
                - silence_segments: Danh sách [start_time, end_time] của silence
                - trimmed_audio: Audio sau khi cắt silence đầu/cuối
                - statistics: Thống kê về âm thanh
                - vad_plot: URL biểu đồ VAD
        """
        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
        except Exception as e:
            print(f"ERROR VAD: {e}")
            data, sr = sf.read(audio_path, dtype='float32')
            y = data if len(data.shape) == 1 else data[:, 0]
        
        duration = len(y) / sr
        
        # 1. Tính Energy (RMS) theo frame
        energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        energy_normalized = energy / np.max(energy) if np.max(energy) > 0 else energy
        
        # 2. Tính ZCR theo frame
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]
        zcr_mean = np.mean(zcr)
        zcr_std = np.std(zcr)
        if zcr_threshold is None:
            zcr_threshold = zcr_mean + 0.5 * zcr_std
        
        # 3. Kết hợp Energy + ZCR để phát hiện voice
        # Voice thường có energy cao hoặc ZCR cao (change quickly)
        energy_voicing = energy_normalized > energy_threshold
        zcr_voicing = zcr > zcr_threshold
        
        # Kết hợp: frame là voice nếu thỏa mãn (energy cao) hoặc (ZCR cao)
        activity = (energy_voicing | zcr_voicing).astype(int)
        
        # 4. Áp dụng smoothing (median filter) để loại bỏ noise spike
        activity_smooth = scipy.signal.medfilt(activity, kernel_size=5)
        
        # 5. Tìm voice segments (bắt đầu/kết thúc)
        # Tính transition: 0→1 là bắt đầu, 1→0 là kết thúc
        activity_padded = np.pad(activity_smooth, (1, 1), constant_values=0)
        transitions = np.diff(activity_padded.astype(int))
        
        starts_indices = np.where(transitions == 1)[0]
        ends_indices = np.where(transitions == -1)[0]
        
        # Convert frame indices to time (seconds)
        times = librosa.frames_to_time(np.arange(len(activity_smooth)), sr=sr, hop_length=hop_length)
        
        segments = []
        for start_idx, end_idx in zip(starts_indices, ends_indices):
            start_time = times[start_idx]
            end_time = times[min(end_idx, len(times) - 1)]
            # Chỉ giữ segments dài ít nhất 0.1 giây
            if end_time - start_time >= 0.1:
                segments.append({
                    'start': float(start_time),
                    'end': float(end_time),
                    'duration': float(end_time - start_time)
                })
        
        # 6. Tìm silence segments (phần còn lại)
        silence_segments = []
        if len(segments) > 0:
            # Silence ở đầu
            if segments[0]['start'] > 0.1:
                silence_segments.append({
                    'start': 0.0,
                    'end': segments[0]['start'],
                    'duration': segments[0]['start']
                })
            # Silence giữa các segments
            for i in range(len(segments) - 1):
                gap_start = segments[i]['end']
                gap_end = segments[i + 1]['start']
                if gap_end - gap_start >= 0.05:
                    silence_segments.append({
                        'start': float(gap_start),
                        'end': float(gap_end),
                        'duration': float(gap_end - gap_start)
                    })
            # Silence ở cuối
            if segments[-1]['end'] < duration - 0.1:
                silence_segments.append({
                    'start': segments[-1]['end'],
                    'end': duration,
                    'duration': duration - segments[-1]['end']
                })
        else:
            # Toàn bộ là silence
            silence_segments.append({
                'start': 0.0,
                'end': duration,
                'duration': duration
            })
        
        # 7. Auto-trim: loại bỏ silence ở đầu/cuối
        if len(segments) > 0:
            trim_start = int(segments[0]['start'] * sr)
            trim_end = int(segments[-1]['end'] * sr)
            trimmed_audio = y[trim_start:trim_end]
        else:
            trimmed_audio = y
        
        # 8. Tạo biểu đồ VAD
        fig, axes = plt.subplots(3, 1, figsize=(14, 8))
        
        # Plot 1: Waveform với VAD overlay
        ax1 = axes[0]
        time_samples = np.arange(len(y)) / sr
        ax1.plot(time_samples, y, linewidth=0.5, color='#1f77b4', alpha=0.7, label='Waveform')
        # Tô màu phần có voice
        for seg in segments:
            ax1.axvspan(seg['start'], seg['end'], alpha=0.2, color='#2ca02c', label='Voice' if seg == segments[0] else '')
        ax1.set_ylabel('Amplitude')
        ax1.set_title('Waveform với Voice Activity Detection', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Energy
        ax2 = axes[1]
        times_frame = librosa.frames_to_time(np.arange(len(energy_normalized)), sr=sr, hop_length=hop_length)
        ax2.plot(times_frame, energy_normalized, linewidth=1.5, color='#ff7f0e', label='Energy (normalized)')
        ax2.axhline(y=energy_threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold: {energy_threshold}')
        ax2.fill_between(times_frame, 0, energy_normalized, where=(energy_voicing > 0), alpha=0.3, color='#2ca02c')
        ax2.set_ylabel('Normalized Energy')
        ax2.set_title('Energy Analysis', fontsize=11)
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Voice Activity
        ax3 = axes[2]
        ax3.fill_between(times_frame, 0, activity_smooth, step='post', alpha=0.6, color='#2ca02c', label='Voice Activity')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Activity')
        ax3.set_ylim([-0.1, 1.1])
        ax3.set_title('Voice Activity Detected', fontsize=11)
        ax3.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        vad_plot_path = Path('static/spectrograms') / f"vad_{np.random.randint(10000, 99999)}.png"
        plt.savefig(vad_plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # 9. Tính thống kê
        total_voice_time = sum(seg['duration'] for seg in segments)
        total_silence_time = sum(seg['duration'] for seg in silence_segments)
        voice_ratio = (total_voice_time / duration * 100) if duration > 0 else 0
        
        return {
            'segments': segments,
            'silence_segments': silence_segments,
            'activity_frames': activity_smooth.tolist(),
            'total_voice_time': float(total_voice_time),
            'total_silence_time': float(total_silence_time),
            'voice_ratio': float(voice_ratio),
            'total_duration': float(duration),
            'num_voice_segments': len(segments),
            'num_silence_segments': len(silence_segments),
            'energy_threshold': float(energy_threshold),
            'zcr_threshold': float(zcr_threshold),
            'vad_plot': f"/static/spectrograms/{vad_plot_path.name}",
            'trimmed_audio_duration': float(len(trimmed_audio) / sr),
            'energy_stats': {
                'mean': float(np.mean(energy_normalized)),
                'std': float(np.std(energy_normalized)),
                'max': float(np.max(energy_normalized))
            },
            'zcr_stats': {
                'mean': float(zcr_mean),
                'std': float(zcr_std),
                'max': float(np.max(zcr))
            }
        }

    def zero_crossing_rate(self, audio_path, frame_length=2048, hop_length=512):
        """
        Tính Zero-Crossing Rate (ZCR) - số lần sóng cắt qua trục 0
        
        ZCR cao → tín hiệu thay đổi nhanh (unvoiced, noise)
        ZCR thấp → tín hiệu thay đổi chậm (voiced, smooth)
        
        Args:
            audio_path: Đường dẫn file audio
            frame_length: Độ dài frame (samples)
            hop_length: Bước nhảy giữa các frame (samples)
            
        Returns:
            dict: ZCR time series, mean ZCR, visualization
        """
        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
        except Exception as e:
            print(f"ERROR ZCR: {e}")
            data, sr = sf.read(audio_path, dtype='float32')
            y = data if len(data.shape) == 1 else data[:, 0]
        
        # Tính ZCR theo frame
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Tính thời gian tương ứng
        times = librosa.frames_to_time(np.arange(len(zcr)), sr=sr, hop_length=hop_length)
        
        # Tính các thống kê
        mean_zcr = float(np.mean(zcr))
        std_zcr = float(np.std(zcr))
        max_zcr = float(np.max(zcr))
        min_zcr = float(np.min(zcr))
        
        # Phân loại voiced/unvoiced dựa trên threshold
        threshold = mean_zcr + 0.5 * std_zcr
        voiced_unvoiced = (zcr > threshold).astype(int).tolist()
        
        # Tạo dữ liệu để hiển thị (giảm số điểm nếu quá nhiều)
        step = max(1, len(zcr) // 200)  # Tối đa 200 điểm
        zcr_data = []
        for i in range(0, len(zcr), step):
            zcr_data.append({
                'time': float(times[i]),
                'zcr': float(zcr[i]),
                'type': 'voiced' if voiced_unvoiced[i] == 0 else 'unvoiced'
            })
        
        # Tạo biểu đồ ZCR
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))
        
        # Plot 1: Waveform
        librosa.display.waveshow(y, sr=sr, ax=ax1, alpha=0.7, color='#1f77b4')
        ax1.set_title('Waveform')
        ax1.set_ylabel('Amplitude')
        
        # Plot 2: ZCR
        ax2.semilogy(times, zcr, linewidth=2, color='#ff7f0e', label='ZCR')
        ax2.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold:.4f})')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Zero-Crossing Rate')
        ax2.set_title('Zero-Crossing Rate Analysis')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        zcr_plot_path = Path('static/spectrograms') / f"zcr_{np.random.randint(10000, 99999)}.png"
        plt.savefig(zcr_plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return {
            'zcr_data': zcr_data,
            'mean_zcr': mean_zcr,
            'std_zcr': std_zcr,
            'max_zcr': max_zcr,
            'min_zcr': min_zcr,
            'threshold': threshold,
            'zcr_plot': f"/static/spectrograms/{zcr_plot_path.name}",
            'description': 'ZCR cao = tín hiệu nhanh (unvoiced), ZCR thấp = tín hiệu chậm (voiced)'
        }

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
