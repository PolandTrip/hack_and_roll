from fastapi import File, UploadFile, Router, HTTPException

router = Router()

async def upload_audio(file: UploadFile = File(...)):
    if file.content_type not in ['audio/wav']:
        raise HTTPException(status_code=400, detail='Invalid File Type')
    
    
    

