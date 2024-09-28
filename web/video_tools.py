import imageio
import base64
import re
import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFont
import io


async def get_cover(video_path):
    reader = imageio.get_reader(video_path)

    for frame in reader:
        res = frame
        break

    reader.close()
    return res.tobytes()


async def bytes2img(bytes):
    return base64.b64encode(bytes).decode('utf-8')


async def change_resolution_and_extension(video_path, new_resolution, new_extension):

    reader = imageio.get_reader(video_path)
    fps = reader.get_meta_data()['fps']

    match = re.search(r"(\d+)p", new_resolution)

    new_height = int(match.group(1))
    new_width = int(new_height * 16 / 9)

    new_video_path = video_path.replace(
        video_path.split('.')[-1], new_extension)
    writer = imageio.get_writer(new_video_path, fps=fps)

    for frame in reader:
        resized_frame = np.array(frame)
        resized_frame = imageio.imresize(
            resized_frame, (new_height, new_width))

        writer.append_data(resized_frame)

    writer.close()
    reader.close()

    return new_video_path
