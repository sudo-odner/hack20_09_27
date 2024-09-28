import os
import uuid
import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile
from covert import STT

app = FastAPI()
stt = STT("base")


@app.get("/upload-video-mp4")
async def upload_video_mp4(file: UploadFile):
    # Check type file
    name, _type = os.path.splitext(file.filename)
    if _type != "mp4":
        return {"status": False, "id": ""}

    absPath = os.path.abspath("")
    # Setting save directory
    pathDict = f"{absPath}/data"
    fileName = f"{uuid.uuid4().hex}.mp4"
    if not os.path.exists(pathDict):
        os.makedirs(pathDict)

    async with aiofiles.open(f"{pathDict}/{fileName}", 'wb') as f:
        content = await file.read()  # async read
        await f.write(content)  # async write

    new_id = stt.convertMP4(pathDict)
    os.rename(f"{pathDict}/{fileName}", f"{pathDict}/{new_id}.mp4")

    return {"status": False, "id": new_id}


@app.get("/video/{id}/text")
def get_text(id: str):

    return {"Hello": "World"}


@app.get("/video/{id}/fragments")
def get_fragment():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)