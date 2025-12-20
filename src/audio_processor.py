import librosa
import numpy as np
import scipy.signal
from pathlib import Path
import soundfile as sf

def isolate_rock_instruments(file_path, upload_dir):
    # 1. Load Audio
    y, sr = librosa.load(file_path, sr=None, mono=False)
    if y.ndim == 1:
        y = np.vstack((y, y))

    # 2. HPSS Stage 1 - Drums (Transients)
    y_harmonic, y_percussive = librosa.effects.hpss(y, margin=(1.0, 3.5))
    y_drums = y_percussive
    
    # 3. Bass (< 140Hz)
    b_low, a_low = scipy.signal.butter(4, 140, btype='low', fs=sr)
    y_bass = scipy.signal.filtfilt(b_low, a_low, y_harmonic, axis=-1)
    
    # Signal without Drums and Bass
    y_rest = y_harmonic - y_bass

    # 4. Vocals (Combined Center + Side vocal range)
    stft_l = librosa.stft(y_rest[0])
    stft_r = librosa.stft(y_rest[1])
    mag_l = np.abs(stft_l)
    mag_r = np.abs(stft_r)
    
    vocal_mask = np.minimum(mag_l, mag_r) / (np.maximum(mag_l, mag_r) + 1e-10)
    vocal_mask = vocal_mask ** 2 
    
    stft_voc = (stft_l + stft_r) / 2 * vocal_mask
    y_vocals_raw = librosa.istft(stft_voc, length=y.shape[1])
    
    b_voc, a_voc = scipy.signal.butter(4, [150, 8000], btype='bandpass', fs=sr)
    y_vocals_mono = scipy.signal.filtfilt(b_voc, a_voc, y_vocals_raw)
    y_vocals = np.vstack((y_vocals_mono, y_vocals_mono))

    # 5. Instruments Residual
    y_inst_total = y_rest - y_vocals
    
    # 6. Separate Guitar vs Keyboard vs Other
    y_inst_harm, y_inst_perc = librosa.effects.hpss(y_inst_total, margin=(1.0, 1.1))
    
    # Guitar: Mid-High range (150Hz - 6000Hz)
    b_gtr, a_gtr = scipy.signal.butter(4, [150, 6000], btype='bandpass', fs=sr)
    y_guitar = scipy.signal.filtfilt(b_gtr, a_gtr, y_inst_total, axis=-1)
    
    # Keyboard / Organ: Residual harmonics (often low-mid or very high air)
    # Focus on non-guitar harmonic components
    y_keys = y_inst_harm - y_guitar
    
    # Other: Residual noise/unclassified
    y_other = y_inst_total - y_guitar - y_keys

    # 7. Final Stems Preparation
    filename = Path(file_path).name
    stem_dir = upload_dir / f"stems_{filename}"
    stem_dir.mkdir(exist_ok=True)
    
    stems_data = {
        "drums": (y_drums, "Drums"),
        "bass": (y_bass, "Bass"),
        "vocals": (y_vocals, "Vocals"),
        "guitar": (y_guitar, "Guitar"),
        "keyboard_organ": (y_keys, "Keyboard / Organ"),
        "other": (y_other, "Other")
    }
    
    response_stems = {}
    for name, (data, label) in stems_data.items():
        # Check if there is significant content (Energy check)
        energy = np.sum(data**2)
        # Threshold to avoid silence/noise being shown as a track
        if energy > 1e-2:
            out_path = stem_dir / f"{name}.wav"
            # Peak normalize
            peak = np.max(np.abs(data))
            if peak > 1e-4:
                data_norm = data / peak * 0.9
            else:
                data_norm = data
            
            sf.write(out_path, data_norm.T, sr)
            response_stems[label] = f"/uploads/stems_{filename}/{name}.wav"
            
    return response_stems
