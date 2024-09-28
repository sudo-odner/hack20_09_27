import re
import base64

import numpy as np
import cv2


async def get_cover(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    _, buffer = cv2.imencode('.jpg', frame)
    return buffer


async def get_duration(video_path):
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps

    cap.release()

    return int(duration * 1000)


async def bytes2img(bytes):
    return base64.b64encode(bytes).decode('utf-8')


async def change_resolution_and_extension(video_path, new_resolution, new_extension):
    r = int(new_resolution[:-1])
    resoluion = (r, r * 16 // 9)

    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if resoluion == (height, width):
        return

    fourcc = cv2.VideoWriter_fourcc(*new_extension.upper())

    out_video_path = '.'.join(video_path.split('.')[:-1]) + '.' + new_extension
    output_video = cv2.VideoWriter(
        out_video_path, fourcc, cap.get(cv2.CAP_PROP_FPS), resoluion)

    while (True):
        ret, frame = cap.read()
        if not ret:
            break

        resized_frame = cv2.resize(
            frame, resoluion, interpolation=cv2.INTER_AREA)

        output_video.write(resized_frame)

    cap.release()
    output_video.release()
