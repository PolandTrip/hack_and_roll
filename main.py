from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import tempfile
from fastapi.middleware.cors import CORSMiddleware
import httpx
from model import interact_with_toaster, text_to_speech, eleven_tts
import base64


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# Define the device control URLs
POWER_ON_URL = "http://172.20.10.2/cm?cmnd=Power%20On"
POWER_OFF_URL = "http://172.20.10.2/cm?cmnd=Power%20Off"


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Endpoint to upload and process audio files.

    Args:
        file (UploadFile): The uploaded audio file.

    Returns:
        dict: A JSON response containing a message and audio file.
    """
    try:
        # Check file content type and extension
        if file.content_type == 'audio/wav' and file.filename.endswith('.wav'):
            # Create a temporary file for the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(await file.read())

            # Pass the temp file path to your processing function
            print(f"Processing file: {temp_file_path}")
            reply = interact_with_toaster(temp_file_path)
            print(reply)

            # Generate TTS audio from the reply
            

            # Perform actions based on the command (e.g., power on/off)
            command = reply.get("command", "unknown")
            async with httpx.AsyncClient() as client:
                 if command == "on":
                     response = await client.get(POWER_ON_URL)
                     print(f"Power On Response: {response.text}")
                 elif command == "off":
                     response = await client.get(POWER_OFF_URL)
                     print(f"Power Off Response: {response.text}")

            # Clean up the temporary input file
            os.remove(temp_file_path)

            #text_to_speech(reply.get("audio_response", ""),"output.wav")
            eleven_tts(reply.get("audio_response", ""))

            # Read and encode the audio file
            # Read and encode the audio file
            with open("output.wav", "rb") as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")

            # Return the text and base64-encoded audio in JSON
            return JSONResponse({
                "message": reply.get("audio_response", ""),
                "command": command,
                "audio_base64": audio_base64
            })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Include the router
app.include_router(router, prefix="/api", tags=["Audio"])
