import os
import base64

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

font_path = "public/RUTUBE_Font/RF_RUTUBE_Bold.ttf"
font = ImageFont.truetype(font_path, 60)


async def get_cover(video_path, timing=0):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    cap.set(cv2.CAP_PROP_POS_FRAMES, timing * fps // 1000)
    _, frame = cap.read()
    cap.release()

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
    if bytes is None:
        return ''.decode('utf-8')
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


async def video2adhd(main_video_dir, main_video, adhd_video):
    top_cap = cv2.VideoCapture(f"{main_video_dir}/{main_video}")
    bottom_cap = cv2.VideoCapture(adhd_video)

    top_width = int(top_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    top_height = int(top_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"{main_video_dir}/out.mp4", fourcc, top_cap.get(
        cv2.CAP_PROP_FPS), (top_width, top_height))

    while top_cap.isOpened():
        ret_top, top_frame = top_cap.read()
        ret_bottom, bottom_frame = bottom_cap.read()

        if ret_top and ret_bottom:
            dim = (top_width, top_height // 2)
            top_frame = cv2.resize(top_frame, dim)
            bottom_frame = cv2.resize(
                bottom_frame, dim, interpolation=cv2.INTER_AREA)

            combined_frame = np.zeros(
                (top_height, top_width, 3), dtype=np.uint8)

            combined_frame[0:top_height // 2, 0:top_width] = top_frame
            combined_frame[top_height // 2:, 0:top_width] = bottom_frame

            out.write(combined_frame)
        else:
            break

    top_cap.release()
    bottom_cap.release()
    out.release()

    os.remove(f"{main_video_dir}/{main_video}")

    os.rename(f"{main_video_dir}/out.mp4", f"{main_video_dir}/{main_video}")


async def cut_video_by_timestamps(video_path, timestamps, out_video_path, subtitles):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_video_path, fourcc, fps,
                          (height, width))

    i = 0
    for timestamp in timestamps:
        start_time, end_time = timestamp.values()
        start_frame = int(start_time * fps / 1000)
        end_frame = int(end_time * fps / 1000)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        frame_count = 0
        while frame_count < (end_frame - start_frame):
            ret, frame = cap.read()
            if not ret:
                break
            while i < len(subtitles) and start_frame + frame_count > int(subtitles[i]['endTime'] * fps / 1000):
                i += 1
            frame_pil = Image.fromarray(frame)
            if i < len(subtitles) and int(subtitles[i]['startTime'] * fps / 1000) <= start_frame + frame_count <= int(subtitles[i]['endTime'] * fps / 1000):
                draw = ImageDraw.Draw(frame_pil)
                text_size = draw.textlength(subtitles[i]['text'], font=font)

                width = frame.shape[1]
                height = frame.shape[0]
                text_x = (width // 2) - (text_size // 2)
                text_y = height - 100

                draw.text((text_x, text_y),
                          subtitles[i]['text'], font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

            out.write(np.array(frame_pil))
            frame_count += 1

    out.release()
    cap.release()
