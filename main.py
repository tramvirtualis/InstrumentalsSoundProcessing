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
from src.isolator import isolate_rock_instruments
from src.effects import apply_audio_effects
from src.analyzer import analyze_audio_features
import uuid

# Resolve NoBackendError for librosa by providing static ffmpeg
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    print("static-ffmpeg not found, please install it.")

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
async def perform_audio_analysis(request: Request):
    data = await request.json()
    filename = data.get("filename")
    
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        analysis_results = analyze_audio_features(file_path, SPECTROGRAM_DIR)
        return JSONResponse(content=analysis_results)
    except Exception as e:
        import traceback
        traceback.print_exc()
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
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"ERROR: {error_msg}")
        traceback.print_exc()
        return JSONResponse(content={"error": f"Separation failed: {error_msg}"}, status_code=500)

@app.post("/process/mix")
async def mix_stems(request: Request):
    data = await request.json()
    stems = data.get("stems")
    print(f"DEBUG: Received mix request with {len(stems) if stems else 0} tracks")
    if not stems:
        raise HTTPException(status_code=400, detail="Stems data is required")
    
    try:
        mix_filename = f"mix_{uuid.uuid4().hex[:8]}.wav"
        output_path = UPLOAD_DIR / mix_filename
        print(f"DEBUG: Output path will be {output_path}")
        
        success = apply_audio_effects(stems, output_path)
        
        if success:
            print(f"DEBUG: Mix successful: {output_path}")
            return JSONResponse(content={
                "message": "Mix complete",
                "mix_url": f"/uploads/{mix_filename}"
            })
        else:
            print("DEBUG: apply_audio_effects returned False")
            return JSONResponse(content={"error": "Failed to create mix - no audio generated"}, status_code=500)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": f"Mixing failed: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
