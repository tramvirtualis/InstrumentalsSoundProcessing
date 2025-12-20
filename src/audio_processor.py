import librosa
import numpy as np
import scipy.signal
from pathlib import Path
import soundfile as sf

def isolate_rock_instruments(file_path, upload_dir):
    print(f"Starting isolation for: {file_path}")
    # 1. Load Audio
    y, sr = librosa.load(file_path, sr=None, mono=False)
    if y.ndim == 1:
        y = np.vstack((y, y))
    total_energy = np.sum(y**2)
    print(f"Audio loaded. Total Energy: {total_energy:.2f}")

    # 2. HPSS Stage 1 - Drums
    print("Extracting drums...")
    y_harmonic, y_percussive = librosa.effects.hpss(y, margin=(1.0, 3.5))
    y_drums = y_percussive
    
    # 3. Bass (< 140Hz)
    b_low, a_low = scipy.signal.butter(4, 140, btype='low', fs=sr)
    y_bass = scipy.signal.filtfilt(b_low, a_low, y_harmonic, axis=-1)
    
    # Residual Harmonic (Vocals + Inst)
    y_res_harm = y_harmonic - y_bass

    # 4. Vocals (Lead + Backing - Center Focus)
    stft_l = librosa.stft(y_res_harm[0])
    stft_r = librosa.stft(y_res_harm[1])
    mag_l = np.abs(stft_l)
    mag_r = np.abs(stft_r)
    
    # Adaptive mask for vocals
    v_mask = np.minimum(mag_l, mag_r) / (np.maximum(mag_l, mag_r) + 1e-10)
    v_mask = v_mask ** 2
    
    stft_voc = (stft_l + stft_r) / 2 * v_mask
    y_voc_mono = librosa.istft(stft_voc, length=y.shape[1])
    # Filter to human voice range
    bv, av = scipy.signal.butter(4, [120, 8000], btype='bandpass', fs=sr)
    y_voc_mono = scipy.signal.filtfilt(bv, av, y_voc_mono)
    y_vocals = np.vstack((y_voc_mono, y_voc_mono))

    # 5. Remaining Instruments
    y_inst = y_res_harm - y_vocals
    
    # 6. Separate Guitar vs Keyboard
    # Strategy: Guitar is more mid-focused (250-4000Hz). 
    # Keyboards/Organs have more sub-harmonics and very high 'chime' (Harmonics).
    # Focus Keyboard on the "stable" side-channel harmonics and specific spectral peaks.
    
    # Split transient/harmonic for instruments
    y_inst_h, y_inst_p = librosa.effects.hpss(y_inst, margin=(1.0, 1.1))
    
    # Guitar Body (200Hz - 4500Hz)
    bg, ag = scipy.signal.butter(4, [200, 4500], btype='bandpass', fs=sr)
    y_guitar = scipy.signal.filtfilt(bg, ag, y_inst_h + y_inst_p, axis=-1)
    
    # Keyboard / Organ (The rest of the instrument signal)
    # Refinement: Keyboard/Organ often lives in the harmonic side-channel.
    y_keys = y_inst - y_guitar

    # 7. Final Stems
    filename = Path(file_path).name
    stem_dir = upload_dir / f"stems_{filename}"
    stem_dir.mkdir(exist_ok=True)
    
    stems_data = {
        "drums": (y_drums, "Drums"),
        "bass": (y_bass, "Bass"),
        "vocals": (y_vocals, "Vocals"),
        "guitar": (y_guitar, "Guitar"),
        "keyboard_organ": (y_keys, "Keyboard / Organ")
    }
    
    response_stems = {}
    for name, (data, label) in stems_data.items():
        try:
            stem_energy = np.sum(data**2)
            # Threshold: More than 0.5% of total audio energy
            if stem_energy > (total_energy * 0.005):
                out_path = stem_dir / f"{name}.wav"
                peak = np.max(np.abs(data))
                if peak > 1e-4:
                    data_norm = data / peak * 0.9
                else:
                    data_norm = data
                
                sf.write(out_path, data_norm.T, sr)
                response_stems[label] = f"/uploads/stems_{filename}/{name}.wav"
                print(f"Saved stem: {label} (Energy: {stem_energy/total_energy:.2%})")
        except Exception as se:
            print(f"Failed to save stem {name}: {se}")
            
    return response_stems
