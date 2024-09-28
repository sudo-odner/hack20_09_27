import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/upload-video")
def upload_video():
    return {"Hello": "World"}


@app.get("/video/{id}/text")
def get_text(id: str):

    return {"Hello": "World"}


@app.get("/video/{id}/fragments")
def get_fragment():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)