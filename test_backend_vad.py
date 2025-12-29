import asyncio
import json
from pathlib import Path
from main import app
from fastapi import Request

# Mock request class
class MockRequest:
    def __init__(self, data):
        self._data = data
        
    async def json(self):
        return self._data

async def test_endpoint():
    print("Testing VAD endpoint...")
    filename = "Dead!  (Frank Iero's Guitar).mp3"
    file_path = Path("uploads") / filename
    
    if not file_path.exists():
        print(f"File {filename} not found in uploads!")
        return

    req = MockRequest({"filename": filename})
    
    try:
        # Import directly from main
        from main import analyze_vad
        
        # Call the endpoint function directly
        response = await analyze_vad(req)
        
        print(f"Status Code: {response.status_code}")
        body = json.loads(response.body)
        print("Response Body keys:", body.keys())
        if "error" in body:
            print("ERROR:", body["error"])
        else:
            print("SUCCESS. Segments found:", body.get("total_segments"))
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoint())
