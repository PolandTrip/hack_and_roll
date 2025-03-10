from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import httpx
import base64
from model import interact_with_toaster, eleven_tts

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


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload and process an audio file."""
    if file.content_type != "audio/wav" or not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav audio files are supported.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(await file.read())

        # Process the uploaded file
        reply = interact_with_toaster(temp_file_path)

        # Generate TTS response
        audio_response = reply.get("audio_response", "")
        eleven_tts(audio_response)

        # Read generated audio file
        with open("output.wav", "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")

        os.remove(temp_file_path)  # Clean up temporary file

        # Execute device control command
        command = reply.get("command")
        if command in DEVICE_URLS:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(DEVICE_URLS[command])
                    print(f"Device {command} Response: {response.text}")
            except httpx.HTTPError as e:
                print(f"Failed to execute device command: {e}")

        return JSONResponse({
            "message": audio_response,
            "command": command,
            "audio_base64": audio_base64
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router
app.include_router(router, prefix="/api", tags=["Audio"])
