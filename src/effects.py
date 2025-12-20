import librosa
import numpy as np
import scipy.signal
from pathlib import Path
import soundfile as sf

def apply_audio_effects(stems_data, output_path):
    print("Starting master mix with effects...")
    master_audio = None
    master_sr = None

    for i, stem in enumerate(stems_data):
        raw_url = stem['url']
        path = raw_url.lstrip('/')
        print(f"Processing track {i+1}/{len(stems_data)}: {path}")
        
        if not Path(path).exists():
            print(f"ERROR: File not found at {path}")
            continue

        try:
            y, sr = librosa.load(path, sr=None, mono=False)
            if y.ndim == 1:
                y = np.vstack((y, y))
            master_sr = sr
        except Exception as e:
            print(f"ERROR: Failed to load {path}: {e}")
            continue
        
        # 1. Speed (Time Stretch)
        if stem.get('speed') and abs(float(stem['speed']) - 1.0) > 0.01:
            rate = float(stem['speed'])
            print(f"Applying Time Stretch: {rate}x")
            y_l = librosa.effects.time_stretch(y[0], rate=rate)
            y_r = librosa.effects.time_stretch(y[1], rate=rate)
            y = np.vstack((y_l, y_r))

        # 2. Pitch Shift
        if stem.get('pitch') and abs(float(stem['pitch'])) > 0.1:
            steps = float(stem['pitch'])
            print(f"Applying Pitch Shift: {steps} semitones")
            y_l = librosa.effects.pitch_shift(y[0], sr=sr, n_steps=steps)
            y_r = librosa.effects.pitch_shift(y[1], sr=sr, n_steps=steps)
            y = np.vstack((y_l, y_r))

        # 3. Distortion (Soft Clipping)
        if stem.get('distortion') and float(stem['distortion']) > 0:
            amount = float(stem['distortion'])
            print(f"Applying distortion ({amount})")
            y = np.tanh(y * (1 + amount * 10))

        # 4. Echo (Delay)
        if stem.get('echo') and float(stem['echo']) > 0:
            amount = float(stem['echo'])
            delay_sec = 0.3
            decay = 0.5 * amount
            delay_samples = int(sr * delay_sec)
            echo_y = np.zeros_like(y)
            if y.shape[1] > delay_samples:
                echo_y[:, delay_samples:] = y[:, :-delay_samples] * decay
                y = y + echo_y

        # 5. Filters (LPF / HPF)
        if stem.get('lpf') and float(stem['lpf']) < 19900:
            b, a = scipy.signal.butter(4, float(stem['lpf']), btype='low', fs=sr)
            y = scipy.signal.filtfilt(b, a, y, axis=-1)
        
        if stem.get('hpf') and float(stem['hpf']) > 30:
            b, a = scipy.signal.butter(4, float(stem['hpf']), btype='high', fs=sr)
            y = scipy.signal.filtfilt(b, a, y, axis=-1)

        # 6. Reverb (Simple Delay-based)
        if stem.get('reverb'):
            delay_samples = int(sr * 0.05)
            decay = 0.4
            reverb_y = np.zeros_like(y)
            if y.shape[1] > delay_samples:
                reverb_y[:, delay_samples:] = y[:, :-delay_samples] * decay
                y = y + reverb_y

        # 7. Panning
        pan = float(stem['pan'])
        left_gain = 1.0 - max(0, pan)
        right_gain = 1.0 - max(0, -pan)
        y[0] = y[0] * left_gain
        y[1] = y[1] * right_gain

        # 8. Volume/Gain
        y = y * float(stem['volume'])

        # Add to master
        if master_audio is None:
            master_audio = y
        else:
            new_len = max(master_audio.shape[1], y.shape[1])
            combined = np.zeros((2, new_len), dtype=np.float32)
            combined[:, :master_audio.shape[1]] += master_audio
            combined[:, :y.shape[1]] += y
            master_audio = combined

    if master_audio is not None:
        peak = np.max(np.abs(master_audio))
        if peak > 1e-4:
            master_audio = master_audio / peak * 0.9
        
        sf.write(output_path, master_audio.T, master_sr)
        print(f"Mix complete. Saved to: {output_path}")
        return True
    return False
