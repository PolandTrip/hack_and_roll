from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
from fastapi.responses import JSONResponse

from model import interact_with_toaster

# Initialize FastAPI app
app = FastAPI()

# Define the router
router = APIRouter()


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Endpoint to upload and process audio files.

    Args:
        file (UploadFile): The uploaded audio file.

    Returns:
        str: A response message or an error.
    """
    try:
        # Check file content type
        if file.content_type == 'audio/wav':
            # Placeholder for additional processing
            reply = interact_with_toaster(file.filename)
            return JSONResponse(content={"message": reply})
        else:
            raise HTTPException(status_code=400, detail="Invalid file type. Only 'audio/wav' is supported.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# Include the router
app.include_router(router, prefix="/api", tags=["Audio"])
