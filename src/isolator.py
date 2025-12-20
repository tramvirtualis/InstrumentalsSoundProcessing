import subprocess
import shutil
import librosa
import numpy as np
import scipy.signal
import soundfile as sf
from pathlib import Path

def isolate_rock_instruments(file_path, upload_dir):
    """
    Main entry point: Tries AI isolation first, falls back to DSP if AI fails.
    """
    print(f"Starting Isolation for: {file_path}")
    
    # 1. Try AI (Demucs)
    try:
        stems = _isolate_ai_demucs(file_path, upload_dir)
        if stems and len(stems) > 0:
            print("AI Isolation successful.")
            return stems
    except Exception as e:
        print(f"AI Isolation failed: {e}. Falling back to DSP...")

    # 2. Fallback to DSP
    print("Executing high-quality DSP fallback...")
    return _isolate_dsp_fallback(file_path, upload_dir)

def _isolate_ai_demucs(file_path, upload_dir):
    filename = Path(file_path).name
    stem_dir = upload_dir / f"stems_{filename}"
    stem_dir.mkdir(exist_ok=True)
    
    tmp_demucs_dir = upload_dir / "demucs_tmp"
    if tmp_demucs_dir.exists():
        shutil.rmtree(tmp_demucs_dir, ignore_errors=True)
    tmp_demucs_dir.mkdir(exist_ok=True)

    print("Running Demucs engine...")
    # Use standard demucs for better stability
    cmd = [
        "python", "-m", "demucs.separate",
        "-n", "htdemucs",
        "--shifts", "1",
        "-j", "2",
        "-o", str(tmp_demucs_dir),
        str(file_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Demucs process error: {result.stderr}")
        return {}

    # Path detection
    model_name = "htdemucs"
    try:
        # Find the actual output folder (Demucs can name it differently based on file name)
        output_base = tmp_demucs_dir / model_name
        track_folder = next(output_base.iterdir())
        
        mapping = {
            "vocals.wav": "Vocals",
            "drums.wav": "Drums",
            "bass.wav": "Bass",
            "other.wav": "Guitar / Sync"
        }

        response_stems = {}
        for src_file, label in mapping.items():
            src = track_folder / src_file
            if src.exists():
                dest = stem_dir / src_file
                shutil.copy2(str(src), str(dest))
                response_stems[label] = f"/uploads/stems_{filename}/{src_file}"
        
        return response_stems
    except Exception as e:
        print(f"Error mapping AI stems: {e}")
        return {}

def _isolate_dsp_fallback(file_path, upload_dir):
    y, sr = librosa.load(file_path, sr=None, mono=False)
    if y.ndim == 1: y = np.vstack((y, y))
    
    # Simple High-Quality DSP Separation
    y_harmonic, y_percussive = librosa.effects.hpss(y, margin=(1.0, 3.0))
    
    # Labels and filters
    stems = {
        "Drums": y_percussive,
        "Vocals": None,
        "Bass": None,
        "Guitar": None,
        "Keyboard / Sync": None
    }
    
    # 1. Bass
    b_low, a_low = scipy.signal.butter(4, 150, btype='low', fs=sr)
    stems["Bass"] = scipy.signal.filtfilt(b_low, a_low, y_harmonic, axis=-1)
    
    # 2. Vocals (Center masking)
    y_mid = y_harmonic - stems["Bass"]
    stft_l = librosa.stft(y_mid[0])
    stft_r = librosa.stft(y_mid[1])
    center_mask = np.minimum(np.abs(stft_l), np.abs(stft_r)) / (np.maximum(np.abs(stft_l), np.abs(stft_r)) + 1e-10)
    stft_voc = (stft_l + stft_r) / 2 * (center_mask ** 4)
    y_voc = librosa.istft(stft_voc, length=y.shape[1])
    stems["Vocals"] = np.vstack((y_voc, y_voc))
    
    # 3. Guitar vs Keyboard Separation (Frequency Banding)
    y_inst = y_mid - stems["Vocals"]
    
    # Guitar Band: 200Hz - 4500Hz
    bg, ag = scipy.signal.butter(4, [200, 4500], btype='bandpass', fs=sr)
    stems["Guitar"] = scipy.signal.filtfilt(bg, ag, y_inst, axis=-1)
    
    # Keys: Remainder
    stems["Keyboard / Sync"] = y_inst - stems["Guitar"]

    # Save
    filename = Path(file_path).name
    stem_dir = upload_dir / f"stems_{filename}"
    stem_dir.mkdir(exist_ok=True)
    
    response = {}
    for label, data in stems.items():
        fname = label.lower().replace(" ", "_").replace("/", "") + ".wav"
        out_path = stem_dir / fname
        peak = np.max(np.abs(data))
        if peak > 1e-4:
            sf.write(out_path, (data / peak * 0.9).T, sr)
            response[label] = f"/uploads/stems_{filename}/{fname}"
            
    return response
