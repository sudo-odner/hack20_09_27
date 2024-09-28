import asyncio
import aiohttp


URL = "http://79.174.95.166/"


async def get_token(video_path):
    async with aiohttp.ClientSession() as session:
        with open(video_path, 'rb') as video_file:
            data = video_file.read()

            headers = {
                'Content-Type': 'multipart/form-data',
                'accept': 'application/json'
            }

            headers = {}
            form = aiohttp.FormData()
            form.add_field('file', data, filename=video_file.name,
                           content_type='video/mp4')

            async with session.post(URL + "upload-video-mp4", data=form, headers=headers) as response:
                data = await response.json()
                return data["id"]


async def get_text(token_model):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL + f"video/{token_model}/text") as response:
            data = await response.json()

            return data["data"]


async def get_fragments(token_model):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL + f"video/{token_model}/fragments") as response:
            data = await response.json()

            return data["data"]
