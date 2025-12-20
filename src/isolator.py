import librosa
import numpy as np
import scipy.signal
from pathlib import Path
import soundfile as sf

def isolate_rock_instruments(file_path, upload_dir):
    print(f"Starting ADVANCED isolation for: {file_path}")
    
    # 1. Load Audio
    y, sr = librosa.load(file_path, sr=None, mono=False)
    if y.ndim == 1:
        y = np.vstack((y, y))
    total_energy = np.sum(y**2)

    # 2. HPSS Stage 1 - Drums (Heavy Transients)
    y_harmonic, y_percussive = librosa.effects.hpss(y, margin=(1.0, 4.0))
    y_drums = y_percussive
    
    # 3. Bass Extraction
    b_low, a_low = scipy.signal.butter(4, 140, btype='low', fs=sr)
    y_bass = scipy.signal.filtfilt(b_low, a_low, y_harmonic, axis=-1)
    
    # Residual Harmonic
    y_mid_high = y_harmonic - y_bass

    # 4. ENHANCED VOCAL EXTRACTION
    print("Applying Enhanced Vocal Extraction...")
    stft_l = librosa.stft(y_mid_high[0])
    stft_r = librosa.stft(y_mid_high[1])
    mag_l = np.abs(stft_l)
    mag_r = np.abs(stft_r)
    
    center_mask = np.minimum(mag_l, mag_r) / (np.maximum(mag_l, mag_r) + 1e-10)
    center_mask = center_mask ** 4
    
    stft_mid = (stft_l + stft_r) / 2 * center_mask
    y_mid_raw = librosa.istft(stft_mid, length=y.shape[1])
    
    y_voc_h, y_voc_p = librosa.effects.hpss(y_mid_raw, margin=(1.0, 2.0))
    
    bv, av = scipy.signal.butter(6, [150, 7000], btype='bandpass', fs=sr)
    y_vocals_clean = scipy.signal.filtfilt(bv, av, y_voc_h)
    y_vocals = np.vstack((y_vocals_clean, y_vocals_clean))

    # 5. Remaining Instruments
    y_inst = y_mid_high - y_vocals
    
    # 6. Guitar vs Keyboard Separation
    bg, ag = scipy.signal.butter(4, [200, 4500], btype='bandpass', fs=sr)
    y_guitar = scipy.signal.filtfilt(bg, ag, y_inst, axis=-1)
    y_keys = y_inst - y_guitar

    # 7. Final Stems Saving
    filename = Path(file_path).name
    stem_dir = upload_dir / f"stems_{filename}"
    stem_dir.mkdir(exist_ok=True)
    
    stems_data = {
        "drums": (y_drums, "Drums"),
        "bass": (y_bass, "Bass"),
        "vocals": (y_vocals, "Vocals"),
        "guitar": (y_guitar, "Guitar"),
        "keyboard_sync": (y_keys, "Keyboard / Sync")
    }
    
    response_stems = {}
    for name, (data, label) in stems_data.items():
        try:
            stem_energy = np.sum(data**2)
            if stem_energy > (total_energy * 0.005):
                out_path = stem_dir / f"{name}.wav"
                peak = np.max(np.abs(data))
                if peak > 1e-4:
                    data_norm = data / peak * 0.9
                else:
                    data_norm = data
                
                sf.write(out_path, data_norm.T, sr)
                response_stems[label] = f"/uploads/stems_{filename}/{name}.wav"
                print(f"Saved stem: {label} (Energy Share: {stem_energy/total_energy:.2%})")
        except Exception as se:
            print(f"Failed to save stem {name}: {se}")
            
    return response_stems
