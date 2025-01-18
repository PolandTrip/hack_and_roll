from fastapi import File, UploadFile, Router, HTTPException
from models.ai import interact_with_toaster

router = Router()

async def upload_audio(file: UploadFile = File(...)):
    if file.content_type in ['audio/wav']:
        reply = interact_with_toaster(file.filename)
        return reply
    raise HTTPException(status_code=400, detail='Invalid File Type')
    
    
    

