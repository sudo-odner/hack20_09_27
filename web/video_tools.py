import os
import base64
import av
import io

import asyncio
import numpy as np
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

    duration = input_container.duration / 1000

    input_container.close()

    return duration


async def bytes2img(bytes):
    if bytes is None:
        return ''.decode('utf-8')
    return base64.b64encode(bytes).decode('utf-8')


async def change_resolution_and_extension(video_path, new_resolution, new_extension, start, end):
    ...


async def video2adhd(main_video_dir, main_video, adhd_video):
    top_container = av.open(f"{main_video_dir}/{main_video}")
    bottom_container = av.open(adhd_video)

    output_container = av.open(f"{main_video_dir}/out.mp4", mode='w')

    top_stream = top_container.streams.video[0]
    bottom_stream = bottom_container.streams.video[0]

    codec_name = top_stream.codec_context.name
    fps = top_stream.codec_context.rate
    out_stream = output_container.add_stream(codec_name, str(fps))
    out_stream.width = top_stream.codec_context.width
    out_stream.height = top_stream.codec_context.height
    out_stream.pix_fmt = top_stream.codec_context.pix_fmt

    in_audio_stream = top_container.streams.audio[0] if top_container.streams.audio else None
    out_audio_stream = None
    if in_audio_stream:
        out_audio_stream = output_container.add_stream(
            in_audio_stream.codec.name, in_audio_stream.codec_context.sample_rate)

    itr = iter(bottom_container.decode(bottom_stream))

    for frame in top_container.decode(top_stream):
        top_frame = frame.to_image()
        bottom_frame = next(itr).to_image()

        top_width, top_height = top_frame.size
        target_height = top_height
        target_width = top_width

        top_frame = top_frame.resize(
            (target_width, target_height // 2), Image.Resampling.LANCZOS)

        bottom_frame = bottom_frame.resize(
            (target_width, target_height // 2), Image.Resampling.LANCZOS)

        combined_frame = Image.new("RGB", (target_width, target_height))

        combined_frame.paste(top_frame, (0, 0))
        combined_frame.paste(bottom_frame, (0, target_height // 2))

        out_frame = av.VideoFrame.from_image(combined_frame)
        out_packet = out_stream.encode(out_frame)
        output_container.mux(out_packet)

    if in_audio_stream:
        top_container.seek(0)
        for packet in top_container.decode(in_audio_stream):
            out_audio_packet = out_audio_stream.encode(packet)
            output_container.mux(out_audio_packet)

    out_packet = out_stream.encode(None)
    output_container.mux(out_packet)

    if out_audio_stream:
        out_audio_packet = out_audio_stream.encode(None)
        output_container.mux(out_audio_packet)

    top_container.close()
    bottom_container.close()
    output_container.close()

    os.remove(f"{main_video_dir}/{main_video}")
    os.rename(f"{main_video_dir}/out.mp4", f"{main_video_dir}/{main_video}")


async def cut_video_by_timestamps(video_path, timestamps, out_video_path, subtitles):
    input_container = av.open(video_path)
    output_container = av.open(out_video_path, mode='w')

    in_video_stream = input_container.streams.video[0]
    codec_name = in_video_stream.codec_context.name
    fps = in_video_stream.codec_context.rate
    out_video_stream = output_container.add_stream(codec_name, str(fps))
    out_video_stream.width = in_video_stream.codec_context.width
    out_video_stream.height = in_video_stream.codec_context.height
    out_video_stream.pix_fmt = in_video_stream.codec_context.pix_fmt

    in_audio_stream = input_container.streams.audio[0] if input_container.streams.audio else None
    out_audio_stream = None
    if in_audio_stream:
        out_audio_stream = output_container.add_stream(
            in_audio_stream.codec.name, in_audio_stream.codec_context.sample_rate)

    i = 0
    for timestamp in timestamps:
        start_time, end_time = timestamp.values()

        input_container.seek(
            int(start_time / 1000 * av.time_base), any_frame=True)

        for frame in input_container.decode(in_video_stream):
            if frame.time * 1000 > end_time:
                break

            while i < len(subtitles) and frame.time * 1000 > subtitles[i]['endTime']:
                i += 1

            frame_pil = frame.to_image()
            if i < len(subtitles) and subtitles[i]['startTime'] <= frame.time * 1000 <= subtitles[i]['endTime']:
                draw = ImageDraw.Draw(frame_pil)
                text_size = draw.textlength(subtitles[i]['text'], font=font)

                width = out_video_stream.width
                height = out_video_stream.height
                text_x = (width // 2) - (text_size // 2)
                text_y = height - 100

                draw.text((text_x, text_y), subtitles[i]['text'], font=font, fill=(
                    255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

            out_frame = av.VideoFrame.from_image(frame_pil)
            out_packet = out_video_stream.encode(out_frame)
            output_container.mux(out_packet)

        if in_audio_stream:
            input_container.seek(
                int(start_time / 1000 * av.time_base), any_frame=True)
            for packet in input_container.decode(in_audio_stream):
                if packet.time * 1000 > end_time:
                    break
                out_audio_packet = out_audio_stream.encode(packet)
                output_container.mux(out_audio_packet)

    out_video_packet = out_video_stream.encode(None)
    output_container.mux(out_video_packet)

    if out_audio_stream:
        out_audio_packet = out_audio_stream.encode(None)
        output_container.mux(out_audio_packet)

    input_container.close()
    output_container.close()


async def update_video(video_path_dir, video_path, timestamps, subtitles):
    await cut_video_by_timestamps(f"{video_path_dir}/{video_path}", timestamps, f"{video_path_dir}/out.mp4", subtitles)

    os.remove(f"{video_path_dir}/{video_path}")
    os.rename(f"{video_path_dir}/out.mp4", f"{video_path_dir}/{video_path}")

# asyncio.run(cut_video_by_timestamps("storage/1/Google — 25 Years in Search_ The Most Searched.mp4",
#             [{"start": 10000.0, "end": 20000.0}], "storage/1/clips/2.mp4", []))
