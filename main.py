import os
import shutil
from pathlib import Path
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

app = FastAPI()

# Directory setup
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR = Path("static")
SPECTROGRAM_DIR = STATIC_DIR / "spectrograms"
SPECTROGRAM_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Instrumental Sound Processing"})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = UPLOAD_DIR / file.filename
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        return JSONResponse(content={"filename": file.filename, "message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/spectrogram")
async def generate_spectrogram(request: Request):
    data = await request.json()
    filename = data.get("filename")
    
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Load audio
        y, sr = librosa.load(file_path, sr=None)
        
        # Calculate spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        # Plot
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        plt.tight_layout()
        
        # Save plot
        output_filename = f"{filename}_spectrogram.png"
        output_path = SPECTROGRAM_DIR / output_filename
        plt.savefig(output_path)
        plt.close()
        
        return JSONResponse(content={
            "spectrogram_url": f"/static/spectrograms/{output_filename}",
            "message": "Spectrogram generated successfully"
        })
    except Exception as e:
        plt.close()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/denoise")
async def denoise_audio(request: Request):
    # Dummy processing for now
    data = await request.json()
    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    # Simulate processing time or return original file as "cleaned" for now
    return JSONResponse(content={"message": "Noise reduction complete (Simulation)", "audio_url": f"/uploads/{filename}"})

@app.post("/analyze/isolation")
async def isolate_instruments(request: Request):
    data = await request.json()
    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # 1. Load Audio
        y, sr = librosa.load(file_path, sr=None, mono=False)
        if y.ndim == 1:
            y = np.vstack((y, y))

        # 2. HPSS for Drums (Aggressive margin to catch huge transients only)
        # percussion_margin > harmonic_margin favors "pure" drums
        y_harmonic, y_percussive = librosa.effects.hpss(y, margin=(1.0, 2.0))
        
        # 3. Bass (Low Pass)
        import scipy.signal
        b, a = scipy.signal.butter(4, 150, btype='low', fs=sr)
        y_bass = scipy.signal.filtfilt(b, a, y_harmonic, axis=-1)
        
        # Residual Harmonic 
        y_harmonic_remain = y_harmonic - y_bass

        # 4. Vocals (Center Channel Approximation)
        y_mid = np.mean(y_harmonic_remain, axis=0)
        y_vocals = np.vstack((y_mid, y_mid))

        # 5. Backing Instruments (Ideally Side channel + Residual Mids)
        y_backing = y_harmonic_remain - y_vocals
        
        # 6. Separate Acoustic vs Electric vs Keys
        # Strategy: 
        # Acoustic Guitar often has percussive strumming (transients) that are softer than drums.
        # Electric Guitar is often sustained and mid-range focused.
        # Keys cover the rest.
        
        # Second Pass HPSS on Backing
        y_back_harm, y_back_perc = librosa.effects.hpss(y_backing, margin=1.0)
        
        # Assign weaker percussive elements to Acoustic Guitar (Strums)
        y_acoustic = y_back_perc
        
        # From the Harmonic Backing, split Electric Guitar vs Keys by Frequency
        # Electric Guitar: 200Hz - 4000Hz Bandpass
        bg, ag = scipy.signal.butter(4, [200, 4000], btype='bandpass', fs=sr)
        y_electric = scipy.signal.filtfilt(bg, ag, y_back_harm, axis=-1)
        
        # Piano/Keys: The remaining spectrum (Deep lows + High Air)
        y_keys = y_back_harm - y_electric

        # 7. Save Stems
        import soundfile as sf
        stem_dir = UPLOAD_DIR / f"stems_{filename}"
        stem_dir.mkdir(exist_ok=True)
        
        stems_data = {
            "drums": (y_percussive.T, "Drums"),
            "bass": (y_bass.T, "Bass"),
            "vocals": (y_vocals.T, "Vocals"),
            "acoustic_guitar": (y_acoustic.T, "Acoustic Guitar"),
            "electric_guitar": (y_electric.T, "Electric Guitar"),
            "piano_keys": (y_keys.T, "Piano / Keyboard")
        }
        
        response_stems = {}
        
        for name, (data, label) in stems_data.items():
            out_path = stem_dir / f"{name}.wav"
            # Normalize to prevent clipping after filtering
            max_val = np.max(np.abs(data))
            if max_val > 1.0:
                data = data / max_val
            
            sf.write(out_path, data, sr)
            response_stems[label] = f"/uploads/stems_{filename}/{name}.wav"
        
        return JSONResponse(content={
            "message": "Instruments isolated successfully", 
            "stems": response_stems
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": f"Separation failed: {str(e)}"}, status_code=500)
