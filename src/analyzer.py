import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
from pathlib import Path

def analyze_audio_features(file_path, spectrogram_dir):
    """
    Performs comprehensive audio analysis:
    1. Basic Info (Duration, SR)
    2. BPM Detection
    3. Key Detection
    4. Spectrogram Generation
    5. Waveform Generation
    """
    y, sr = librosa.load(file_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    
    # 1. BPM Detection
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = round(float(tempo), 2)
    
    # 2. Key Detection (Chroma-based)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_avg = np.mean(chroma, axis=1)
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key_idx = np.argmax(chroma_avg)
    detected_key = keys[key_idx]
    
    # 3. Spectrogram
    plt.figure(figsize=(10, 4))
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Log-Frequency Spectrogram')
    plt.tight_layout()
    
    spec_filename = f"{Path(file_path).name}_spec.png"
    spec_path = spectrogram_dir / spec_filename
    plt.savefig(spec_path, transparent=True)
    plt.close()
    
    # 4. Waveform
    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr, alpha=0.5)
    plt.title('Waveform Envelope')
    plt.tight_layout()
    
    wave_filename = f"{Path(file_path).name}_wave.png"
    wave_path = spectrogram_dir / wave_filename
    plt.savefig(wave_path, transparent=True)
    plt.close()
    
    return {
        "bpm": bpm,
        "key": detected_key,
        "duration": round(duration, 2),
        "sample_rate": sr,
        "spectrogram_url": f"/static/spectrograms/{spec_filename}",
        "waveform_url": f"/static/spectrograms/{wave_filename}"
    }
