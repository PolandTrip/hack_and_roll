from fastapi import File, UploadFile, APIRouter, HTTPException
from models.ai import interact_with_toaster

router = APIRouter()

async def upload_audio(file: UploadFile = File(...)):
    if file.content_type in ['audio/wav']:
        raise HTTPException(status_code=400, detail='Invalid File Type')

    reply = interact_with_toaster(file.filename)
    return reply
    
    
    

