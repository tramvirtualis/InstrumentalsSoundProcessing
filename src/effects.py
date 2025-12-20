import librosa
import numpy as np
import scipy.signal
from pathlib import Path
import soundfile as sf
import os

def apply_audio_effects(stems_data, output_path):
    print(f"--- Starting Render Mix ({len(stems_data)} tracks) ---")
    master_audio = None
    master_sr = 44100 # Default

    root_dir = Path(os.getcwd())

    for i, stem in enumerate(stems_data):
        raw_url = stem.get('url', '')
        if not raw_url:
            print(f"Track {i}: No URL provided, skipping.")
            continue
            
        # Fix path
        rel_path = raw_url.lstrip('/')
        file_path = root_dir / rel_path
        
        print(f"Track {i}: Loading {file_path}")
        if not file_path.exists():
            print(f"ERROR: File NOT FOUND at {file_path}")
            continue

        try:
            y, sr = librosa.load(str(file_path), sr=None, mono=False)
            if y.ndim == 1:
                y = np.vstack((y, y))
            master_sr = sr
            print(f"  Loaded successfully. Duration: {y.shape[1]/sr:.2f}s, SR: {sr}")
        except Exception as e:
            print(f"ERROR: Failed to load {file_path}: {e}")
            continue
        
        # 1. Speed (Time Stretch)
        speed = float(stem.get('speed', 1.0))
        if abs(speed - 1.0) > 0.01:
            print(f"  Effect: Speed {speed}x")
            y_l = librosa.effects.time_stretch(y[0], rate=speed)
            y_r = librosa.effects.time_stretch(y[1], rate=speed)
            y = np.vstack((y_l, y_r))

        # 2. Pitch Shift
        pitch = float(stem.get('pitch', 0))
        if abs(pitch) > 0.1:
            print(f"  Effect: Pitch {pitch} semitones (Wait, this is slow CPU work...)")
            y_l = librosa.effects.pitch_shift(y[0], sr=sr, n_steps=pitch)
            y_r = librosa.effects.pitch_shift(y[1], sr=sr, n_steps=pitch)
            y = np.vstack((y_l, y_r))

        # 3. Distortion
        dist = float(stem.get('distortion', 0))
        if dist > 0.01:
            print(f"  Effect: Distortion {dist}")
            y = np.tanh(y * (1 + dist * 5))

        # 4. Echo
        echo = float(stem.get('echo', 0))
        if echo > 0.01:
            print(f"  Effect: Echo {echo}")
            delay_samples = int(sr * 0.3)
            decay = 0.5 * echo
            echo_y = np.zeros_like(y)
            if y.shape[1] > delay_samples:
                echo_y[:, delay_samples:] = y[:, :-delay_samples] * decay
                y = (y + echo_y)

        # 5. Filters
        lpf = float(stem.get('lpf', 20000))
        if lpf < 19500:
            print(f"  Effect: LPF {lpf}Hz")
            b, a = scipy.signal.butter(4, min(lpf, sr/2-1), btype='low', fs=sr)
            y = scipy.signal.filtfilt(b, a, y, axis=-1)
        
        hpf = float(stem.get('hpf', 20))
        if hpf > 30:
            print(f"  Effect: HPF {hpf}Hz")
            b, a = scipy.signal.butter(4, min(hpf, sr/2-1), btype='high', fs=sr)
            y = scipy.signal.filtfilt(b, a, y, axis=-1)

        # 6. Reverb
        reverb = float(stem.get('reverb', 0))
        if reverb > 0.01:
            print(f"  Effect: Reverb {reverb}")
            delay = int(sr * 0.05)
            y_padded = np.pad(y, ((0, 0), (0, delay)))
            y = y_padded[:, :y.shape[1]] + y_padded[:, delay:] * (0.4 * reverb)

        # 7. Volume & Pan
        vol = float(stem.get('volume', 1.0))
        pan = float(stem.get('pan', 0.0))
        left_gain = vol * (1.0 - max(0, pan))
        right_gain = vol * (1.0 - max(0, -pan))
        y[0] *= left_gain
        y[1] *= right_gain

        # Add to master
        if master_audio is None:
            master_audio = y
        else:
            # Handle different lengths
            new_len = max(master_audio.shape[1], y.shape[1])
            combined = np.zeros((2, new_len), dtype=np.float32)
            combined[:, :master_audio.shape[1]] += master_audio
            combined[:, :y.shape[1]] += y
            master_audio = combined

    if master_audio is not None:
        # Final Norm
        peak = np.max(np.abs(master_audio))
        if peak > 1e-4:
            master_audio = master_audio / peak * 0.95
        
        sf.write(output_path, master_audio.T, master_sr)
        print(f"Successfully rendered mix to {output_path}")
        return True
    
    print("ERROR: No audio tracks were successfully processed.")
    return False
