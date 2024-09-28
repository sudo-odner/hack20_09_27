import os
import shutil
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db_tools import queries
import video_tools


class App(FastAPI):
    def __init__(self):
        super().__init__()

        self.add_api_route("/api/get_projects",
                           self.get_projects, methods=["GET"])
        self.add_api_route("/api/create_project",
                           self.create_project, methods=["POST"])
        self.add_api_route(
            "/api/get_clips/{project_id}", self.get_clips, methods=["GET"])
        self.add_api_route(
            "/api/get_clip_details/{clip_id}", self.get_clip_details, methods=["GET"])
        self.add_api_route(
            "/api/get_clip/{clip_id}", self.get_clip, methods=["GET"])
        self.add_api_route(
            "/api/update_clip/{clip_id}", self.update_clip, methods=["PATCH"])
        self.add_api_route(
            "/api/export_clip/{clip_id}", self.export_clip, methods=["GET"])
        self.add_api_route(
            "/api/remove_clip/{clip_id}", self.remove_clip, methods=["DELETE"])

    async def get_projects(self, request: Request):
        projects = await queries.get_projects(request.client.host)

        res = []
        for project in projects:
            res.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "cover": await video_tools.bytes2img(project.cover),
                    "datetime": str(project.datetime)
                }
            )

        return JSONResponse(res)

    async def create_project(self, request: Request, file: UploadFile = File(...), name: str = Form(...)):
        project_id = await queries.create_project(request.client.host, name)

        filename = file.filename
        os.makedirs(f"storage/{project_id}", exist_ok=True)
        with open(f"storage/{project_id}/{filename}", "wb") as f:
            content = await file.read()
            f.write(content)

        cover = await video_tools.get_cover(f"storage/{project_id}/{filename}")
        await queries.set_cover_project(project_id, cover)

        os.makedirs(f"storage/{project_id}/clips", exist_ok=True)
        duration = await video_tools.get_duration(f"storage/{project_id}/{filename}")
        clip_id = await queries.create_clip(project_id, filename, duration, cover)

        shutil.copy2(f"storage/{project_id}/{filename}",
                     f"storage/{project_id}/clips/{clip_id}.mp4")

        return JSONResponse({"project_id": project_id}, 201)

    async def get_clips(self, project_id: int):
        clips_id = await queries.get_clips_id(project_id)

        return JSONResponse(clips_id)

    async def get_clip_details(self, clip_id: int):
        cover, title, duration = await queries.get_clip_details(clip_id)

        return JSONResponse({"cover": await video_tools.bytes2img(cover), "title": title, "duration": duration})

    async def get_clip(self, clip_id: int):
        clip, project_id = await queries.get_clip(clip_id)

        with open(f"storage/{project_id}/clips/{clip.id}.mp4", "rb") as f:
            video = f.read()
        video = await video_tools.bytes2img(video)

        return JSONResponse({"video": video, "subtitles": clip.subtitles, "tags": clip.tags, "start": clip.start, "end": clip.end, "subtitle": clip.subtitle, "adhd": clip.adhd})

    async def update_clip(self, clip_id: int, subtitle: bool, adhd: bool):
        await queries.update_clip(clip_id, subtitle, adhd)

        return JSONResponse({"status": "ok"})

    async def export_clip(self, clip_id: int, resolution: str, start: str, end: str, extension: str):
        clip = await queries.get_clip(clip_id)

        await video_tools.change_resolution_and_extension(f"storage/{clip.project_id}/clips/{clip.id}.mp4", resolution, extension)

        with open(f"storage/{clip.project_id}/clips/{clip.id}.{extension}", "rb") as f:
            video = f.read()

        return JSONResponse({"video": video})

    async def remove_clip(self, clip_id: int):
        await queries.remove_clip(clip_id)

        return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    app = App()

    origins = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if os.getenv('DOCKER_CONTAINER'):
        host = "app_web"
    else:
        host = 'localhost'
    uvicorn.run(app, host=host, port=8000)
