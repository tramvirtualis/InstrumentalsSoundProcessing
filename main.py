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

# Import custom modules
from src.audio_processor import isolate_rock_instruments

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
        y, sr = librosa.load(file_path, sr=None)
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        plt.tight_layout()
        
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
    data = await request.json()
    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
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
        response_stems = isolate_rock_instruments(file_path, UPLOAD_DIR)
        
        return JSONResponse(content={
            "message": "Rock Instruments isolation complete", 
            "stems": response_stems
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": f"Separation failed: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
