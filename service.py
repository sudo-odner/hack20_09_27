import os
import uuid
import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile

from analysis import text_analysis, audio_analysis, video_analysis, get_overal
from covert import STT, SentimentAnalysis

app = FastAPI()
stt = STT("base")
sa = SentimentAnalysis()


@app.post("/upload-video-mp4")
async def upload_video_mp4(file: UploadFile):
    # Check type file
    name, _type = file.filename.split(".")
    if _type != "mp4":
        print(file.filename)
        return {"status": False, "id": ""}

    absPath = os.path.abspath("")
    # Setting save directory
    pathDict = f"{absPath}/user/data"
    fileName = f"{uuid.uuid4().hex}.mp4"
    if not os.path.exists(pathDict):
        os.makedirs(pathDict)

    async with aiofiles.open(f"{pathDict}/{fileName}", 'wb') as f:
        content = await file.read()  # async read
        await f.write(content)  # async write

    new_id = stt.convertMP4(f"{pathDict}/{fileName}")
    os.rename(f"{pathDict}/{fileName}", f"{pathDict}/{new_id}.mp4")

    return {"status": True, "id": new_id}


@app.get("/video/{_id}/text")
def get_text(_id: str):
    _, wordData, status = stt.loadData(_id)
    return {"status": status, "data": wordData}


@app.get("/video/{_id}/fragments")
def get_fragment(_id: str):
    absPath = os.path.abspath("")
    pathDict = f"{absPath}/user"

    _, word_data, status = stt.loadData(_id)
    if not status:
        return {"status": False}

    pathMP4 = os.path.abspath(f"{pathDict}/data/{_id}.mp4")
    sa.sentimentWordData(word_data)

    # Create three data analiz text, audio, video
    dataText = text_analysis(word_data)
    dataAudio = audio_analysis(pathMP4)
    dataVideo = video_analysis(pathMP4)

    # Merge data and get best timing
    overal = get_overal(dataText, dataAudio, dataVideo)

    # Add emotion people(emoji)

    print(overal)
    return {"status": True}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)
