from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import httpx
import base64
from model import interact_with_toaster, eleven_tts
import asyncio

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Device control URLs
DEVICE_URLS = {
    "on": "http://172.20.10.2/cm?cmnd=Power%20On",
    "off": "http://172.20.10.2/cm?cmnd=Power%20Off",
}

async def send_device_command(command: str):
    """Send device command asynchronously if valid."""
    if command in DEVICE_URLS:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(DEVICE_URLS[command])
                print(f"Device '{command}' response: {response.text}")
        except httpx.HTTPError as e:
            print(f"Device command failed: {e}")

def read_audio_base64_sync(filepath: str) -> str:
    """Read audio file and return base64-encoded string (blocking)."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    if file.content_type != "audio/wav" or not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav audio files are supported.")

    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(contents)

        reply = interact_with_toaster(temp_file_path)
        os.remove(temp_file_path)

        audio_response = reply.get("audio_response")
        if not audio_response:
            raise ValueError("No audio_response in reply.")

        command = reply.get("command")

        # Run TTS and device command in parallel
        await asyncio.gather(
            asyncio.to_thread(eleven_tts, audio_response),  # run sync function in thread
            send_device_command(command)
        )

        # Read and encode output.wav in thread to avoid blocking
        audio_base64 = await asyncio.to_thread(read_audio_base64_sync, "output.wav")

        return JSONResponse({
            "message": audio_response,
            "command": command,
            "audio_base64": audio_base64
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

def _read_audio_base64_sync(filepath: str) -> str:
    """Sync fallback for reading base64 from file."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Include the router
app.include_router(router, prefix="/api", tags=["Audio"])
