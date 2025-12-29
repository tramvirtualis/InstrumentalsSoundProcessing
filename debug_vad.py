import librosa
import numpy as np
from pathlib import Path
import traceback

def test_vad():
    file_path = Path("uploads") / "Dead!  (Frank Iero's Guitar).mp3"
    print(f"Testing VAD on: {file_path}")
    if not file_path.exists():
        print("File does not exist!")
        return

    try:
        print("Loading audio...")
        y, sr = librosa.load(str(file_path), sr=None)
        print(f"Loaded: {len(y)} samples, sr={sr}")
        
        print("Trimming...")
        y_trimmed, index = librosa.effects.trim(y, top_db=30)
        print(f"Trimmed index: {index}")
        
        print("Splitting...")
        intervals = librosa.effects.split(y, top_db=30)
        print(f"Found {len(intervals)} segments")
        
        for i, (start, end) in enumerate(intervals[:5]):
            print(f"Segment {i+1}: {start/sr:.2f}s - {end/sr:.2f}s")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_vad()
