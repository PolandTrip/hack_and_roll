from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
import httpx
from model import interact_with_toaster

# Initialize FastAPI app
app = FastAPI()

# Define the router
router = APIRouter()

# Define the device control URLs
POWER_ON_URL = "http://192.168.1.27/cm?cmnd=Power%20On"
POWER_OFF_URL = "http://192.168.1.27/cm?cmnd=Power%20Off"


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Endpoint to upload and process audio files.

    Args:
        file (UploadFile): The uploaded audio file.

    Returns:
        dict: A JSON response containing a message or an error.
    """
    try:
        # Check file content type and extension
        if file.content_type == 'audio/wav' and file.filename.endswith('.wav'):
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file_path = temp_file.name
                # Write uploaded file contents to the temporary file
                temp_file.write(await file.read())

            # Pass the temp file path to your processing function
            print(f"Processing file: {temp_file_path}")
            reply = interact_with_toaster(temp_file_path)

            # Optionally, clean up the temporary file after processing
            os.remove(temp_file_path)

            # Extract the command from the reply
            command = reply.get("command", "unknown")
            print(f"Command received: {command}")

            # Perform the corresponding action based on the command
            async with httpx.AsyncClient() as client:
                if command == "on":
                    response = await client.get(POWER_ON_URL)
                    print(f"Power On Response: {response.text}")
                elif command == "off":
                    response = await client.get(POWER_OFF_URL)
                    print(f"Power Off Response: {response.text}")

            # Return the reply message
            return JSONResponse(content={"message": reply.get("audio_response", "No audio response provided.")})
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only '.wav' files with content type 'audio/wav' are supported."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Include the router
app.include_router(router, prefix="/api", tags=["Audio"])
