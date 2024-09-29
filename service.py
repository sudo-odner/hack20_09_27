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

# Создание экземпляра FastAPI
app = FastAPI()

# Инициализация объектов для обработки речи и анализа тональности
stt = STT("base")
sa = SentimentAnalysis()


# Определение POST маршрута для загрузки видео
@app.post("/upload-video-mp4")
async def upload_video_mp4(file: UploadFile):
    # Логируем начало загрузки видео
    print("Start video upload")

    # Проверяем тип файла (должен быть .mp4)
    name, _type = file.filename.split(".")
    if _type != "mp4":
        print(file.filename)
        return {"status": False, "id": ""}

    # Получаем абсолютный путь к директории
    absPath = os.path.abspath("")

    # Устанавливаем директорию для сохранения файла
    pathDict = f"{absPath}/user/data"
    fileName = f"{uuid.uuid4().hex}.mp4"
    # Создаем директорию, если она не существует
    if not os.path.exists(pathDict):
        os.makedirs(pathDict)

    # Асинхронно открываем файл для записи
    async with aiofiles.open(f"{pathDict}/{fileName}", 'wb') as f:
        # Читаем контент файла асинхронно
        content = await file.read()
        # Записываем контент файла асинхронно
        await f.write(content)

    # Конвертируем видео, сохраняем и получаем уникальный id (выполняется распознавание речи)
    new_id = stt.convertMP4(f"{pathDict}/{fileName}")

    # Переименовываем файл с видео, используя новый id
    os.rename(f"{pathDict}/{fileName}", f"{pathDict}/{new_id}.mp4")
    return {"status": True, "id": new_id}


# Определение GET маршрута для получения текста и атайм кодов видео по идентификатору
@app.get("/video/{_id}/text")
def get_text(_id: str):
    # Логируем начало процесса создания текста
    print("Start create text video")
    # Загружаем данные видео по идентификатору
    _, wordData, status = stt.loadData(_id)
    # Логируем завершение создания текста
    print("End create fragments video: ", wordData, status)
    # Возвращаем статус и данные текста
    return {"status": status, "data": wordData}


# Определение POST маршрута для генерации заголовков и тегов для текста
@app.post("/info_fragments")
def info_fragments(text: list[dict]):
    allText = ""
    for text in text:
        text = text.get("text")
        if type(text) == "str":
            allText = "".join(allText, text)
        else:
            print("text in dict has error")

    # Генерация заголовка и описания на основе текста
    title, about = generate_text_data(allText, num_keywords=1, num_sentences=3)
    tags = generate_tags(allText)
    # Возвращаем статус, теги, заголовок и описание
    return {"status": True, "tags": tags, "title": title, "about": about}


# Определение GET маршрута для получения фрагментов видео по идентификатору
@app.get("/video/{_id}/fragments")
def get_fragment(_id: str):
    startTime = time.time()
    # Логируем начало создания фрагментов видео
    print("Start create fragments video")
    # Определяем абсолютный путь к директории
    absPath = os.path.abspath("")
    pathDict = f"{absPath}/user"

    # Загружаем данные видео по идентификатору
    _, word_data, status = stt.loadData(_id)
    if not status:
        return {"status": False}

    # Определяем путь к видеофайлу
    pathMP4 = os.path.abspath(f"{pathDict}/data/{_id}.mp4")
    # Анализируем текст с использованием анализа тональности
    sa.sentimentWordData(word_data)

    # Анализируем текст, аудио и видео
    timeText = time.time()
    dataText = text_analysis(word_data)
    print("timeText: ", time.time() - timeText)
    timeAudio = time.time()
    dataAudio = audio_analysis(pathMP4)
    print("timeAudio: ", time.time() - timeAudio)
    timeVideo = time.time()
    dataVideo = video_analysis(pathMP4)
    print("timeVideo: ", time.time() - timeVideo)

    # Объединяем данные и получаем лучшие таймкоды для фрагментов
    timeMerge = time.time()
    print("Start merge data")
    fragment = get_timecodes(dataText, dataVideo, dataAudio, aud_c=1, compl_c=0.5, k=1, points_between_peaks=800,
                             epsilon_to_cut=500)
    # Формируем список ответов с началом и концом каждого фрагмента
    answer_dict = list()
    for data in fragment:
        answer_dict.append({
            "startTime": data[0][0],
            "endTime": data[0][1],
        })
    # Логируем время выполнения объединения и общий процесс создания фрагментов
    print("timeMerge: ", time.time() - timeMerge)
    print("time fragment: ", time.time() - startTime)
    print("End create fragments video: ", fragment, answer_dict)
    return {"status": True, "data": answer_dict}


# Запуск приложения FastAPI на указанном хосте и порте
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
