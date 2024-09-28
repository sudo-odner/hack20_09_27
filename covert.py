from typing import List

import whisper_timestamped as whisper  # For convert to text, STT (Speach to text)
import torch  # For whisper
from moviepy.editor import VideoFileClip  # For convert MP4 to MP3
import uuid  # For generate id to user video data
import pickle  # Save user video data on file
import os  # Work with file
import numpy as np  # Fast work with array
from transformers import pipeline  # Get open-source model


class STT:
    def __init__(self, modelType="base"):
        self.modelType = modelType
        self.batch_size = 16  # reduce if low on GPU mem
        self.divice = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if torch.cuda.is_available() else "int8"
        self.model = whisper.load_model(self.modelType, device=self.divice)

    def convertMP3ToText(self, pathToMP3: str) -> (str, str):
        audio = whisper.load_audio(pathToMP3)
        result = whisper.transcribe(self.model, audio, language="ru")

        text: str = result["text"]
        word_data: list[dict] = list()
        for segment in result["segments"]:
            for word in segment["words"]:
                word_data.append({
                    "text": word["text"],
                    "startTime": word["start"] * 1000,
                    "endTime": word["end"] * 1000
                })
        return text, word_data

    def saveData(self, text: str, word_data: str) -> str:
        absPath = os.path.abspath("")

        # Saving data
        saveData = {
            "text": text,
            "word_data": word_data
        }

        # Setting save directory
        pathDict = f"{absPath}/user"
        if not os.path.exists(pathDict):
            os.makedirs(pathDict)

        # Create id user video
        _id = uuid.uuid4().hex
        while os.path.isfile(f"{pathDict}/{_id}.pickle"):
            _id = uuid.uuid4().hex

        # Save data in pickle
        with open(f"{pathDict}/{_id}.pickle", 'wb') as file:
            pickle.dump(saveData, file, protocol=pickle.HIGHEST_PROTOCOL)
        return _id

    def loadData(self, _id: str) -> (str, list[dict]):
        absPath = os.path.abspath("")
        pathDict = f"{absPath}/user"

        # Check created file
        if not os.path.isfile(f"{pathDict}/{_id}.pickle"):
            print("File does not exist")
            return "", list()

        # Open file
        with open(f"{pathDict}/{_id}.pickle", 'rb') as file:
            data = pickle.load(file)

        return data["text"], data["word_data"]

    def convertMP3(self, pathToMP3: str) -> str:
        text, word_data = self.convertMP3ToText(pathToMP3)
        _id = self.saveData(text, word_data)
        return _id

    def convertMP4(self, pathToMP4: str) -> str:
        absPath = os.path.abspath("")
        pathTempMP3 = f"{absPath}/temp/mp3"
        fileName = os.path.splitext(os.path.basename(pathToMP4))[0]
        tempFilePath = f"{pathTempMP3}/{fileName}.mp3"

        # Setting temp directory
        if not os.path.exists(pathTempMP3):
            os.makedirs(pathTempMP3)

        # Convert MP4 to MP3
        video = VideoFileClip(pathToMP4)
        video.audio.write_audiofile(tempFilePath, logger=None)

        # Convert MP3 to data text
        _id = self.convertMP3(tempFilePath)

        # Delete temp file MP3
        if os.path.exists(tempFilePath):
            os.remove(tempFilePath)

        return _id


class SentimentAnalysis:
    def __init__(self):
        self.classifier = pipeline('sentiment-analysis', model="cointegrated/rubert-tiny-sentiment-balanced")

    def _sentimentText(self, text: str) -> float:
        result = self.classifier(text)[0]
        # Преобразование результатов в числовую шкалу
        if result['label'] in ('positive', 'negative'):
            return result['score']  # Позитивные эмоции — от 0 до 1
        else:
            return 0.0  # Нейтральный тон = 0

    def sentimentWordData(self, wordData: list[dict], lenWords: int = 10) -> list[dict]:
        # Data scope with sentiment for ever word
        dataScope = np.zeros(len(wordData) + lenWords * 2)
        # Create zero value form start and end array
        zeroWordData = [{"text": ""} for idx in range(lenWords)]
        # New word data
        wordData = zeroWordData + wordData + zeroWordData

        for idx in range(len(wordData) - lenWords):
            # Create text to sentiment score
            text = "".join([word["text"] for word in wordData[idx:idx + lenWords]])
            sentimentScore = self._sentimentText(text)

            # Add score
            dataScope[idx:idx + lenWords] += sentimentScore

        dataScope = dataScope / lenWords

        for idx in range(len(dataScope)):
            wordData[idx]["sentiment_analysis"] = dataScope[idx]

        return wordData[lenWords:(len(wordData) - lenWords)]
