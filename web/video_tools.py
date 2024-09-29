import os
import base64
import av
import io

import asyncio
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

font_path = "public/RUTUBE_Font/RF_RUTUBE_Bold.ttf"
font = ImageFont.truetype(font_path, 60)


async def get_cover(video_path, timing=0):
    input_container = av.open(video_path)

    in_stream = input_container.streams.video[0]

    input_container.seek(int(timing / 1000 * av.time_base))

    for frame in input_container.decode(in_stream):
        img = frame.to_image()
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        input_container.close()
        return buffer.getvalue()


async def get_duration(video_path):
    input_container = av.open(video_path)

    in_stream = input_container.streams.video[0]

    duration = in_stream.duration * av.time_base

    input_container.close()

    return int(duration * 1000)


async def bytes2img(bytes):
    if bytes is None:
        return ''.decode('utf-8')
    return base64.b64encode(bytes).decode('utf-8')


async def change_resolution_and_extension(video_path, new_resolution, new_extension):
    ...


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
    input_container = av.open(video_path)
    output_container = av.open(out_video_path, mode='w')

    in_stream = input_container.streams.video[0]

    codec_name = in_stream.codec_context.name
    fps = in_stream.codec_context.rate
    out_stream = output_container.add_stream(codec_name, str(fps))
    out_stream.width = in_stream.codec_context.width
    out_stream.height = in_stream.codec_context.height
    out_stream.pix_fmt = in_stream.codec_context.pix_fmt

    i = 0
    for timestamp in timestamps:
        start_time, end_time = timestamp.values()

        input_container.seek(int(start_time / 1000 * av.time_base))

        for frame in input_container.decode(in_stream):
            if frame.time * 1000 > end_time:
                continue

            while i < len(subtitles) and frame.time * 1000 > subtitles[i]['endTime']:
                i += 1
            frame_pil = frame.to_image()
            if i < len(subtitles) and subtitles[i]['startTime'] <= frame.time * 1000 <= subtitles[i]['endTime']:
                draw = ImageDraw.Draw(frame_pil)
                text_size = draw.textlength(subtitles[i]['text'], font=font)

                width = out_stream.width
                height = out_stream.height
                text_x = (width // 2) - (text_size // 2)
                text_y = height - 100

                draw.text((text_x, text_y),
                          subtitles[i]['text'], font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

            out_frame = av.VideoFrame.from_image(frame_pil)
            out_packet = out_stream.encode(out_frame)
            output_container.mux(out_packet)

    out_packet = out_stream.encode(None)
    output_container.mux(out_packet)

    input_container.close()
    output_container.close()
