import os
import time
import uuid
import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile

from analysis import text_analysis, audio_analysis, video_analysis, get_timecodes
from covert import STT, SentimentAnalysis
from generate import generate_tags
from generateNameAndDisc import generate_text_data

app = FastAPI()
stt = STT("base")
sa = SentimentAnalysis()


@app.post("/upload-video-mp4")
async def upload_video_mp4(file: UploadFile):
    print("Start video upload")
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
    print("Start create text video")
    _, wordData, status = stt.loadData(_id)
    print("End create fragments video: ", wordData, status)
    return {"status": status, "data": wordData}


@app.post("/info_fragments")
def info_fragments(text: str):
    title, about = generate_text_data(text, num_keywords=1, num_sentences=3)
    return {"status": True, "tags": generate_tags(text), "title": title, "about": about}


@app.get("/video/{_id}/fragments")
def get_fragment(_id: str):
    startTime = time.time()
    print("Start create fragments video")
    absPath = os.path.abspath("")
    pathDict = f"{absPath}/user"

    _, word_data, status = stt.loadData(_id)
    if not status:
        return {"status": False}

    pathMP4 = os.path.abspath(f"{pathDict}/data/{_id}.mp4")
    sa.sentimentWordData(word_data)

    # Create three data analiz text, audio, video
    timeText = time.time()
    dataText = text_analysis(word_data)
    print("timeText: ", time.time() - timeText)
    timeAudio = time.time()
    dataAudio = audio_analysis(pathMP4)
    print("timeAudio: ", time.time() - timeAudio)
    timeVideo = time.time()
    dataVideo = video_analysis(pathMP4)
    print("timeVideo: ", time.time() - timeVideo)

    # Merge data and get best timing
    timeMerge = time.time()
    print("Start merge data")
    fragment = get_timecodes(dataText, dataVideo, dataAudio, aud_c=1, compl_c=0.5, k=1, points_between_peaks=800, epsilon_to_cut=500)
    answer_dict = list()
    for data in fragment:
        answer_dict.append({
            "startTime": data[0][0],
            "endTime": data[0][1],
        })
    print("timeMerge: ", time.time() - timeMerge)
    print("time fragment: ", time.time() - startTime)
    print("End create fragments video: ", fragment, answer_dict)
    return {"status": True, "data": answer_dict}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
