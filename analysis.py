import cv2
import librosa
import numpy as np
import scipy
from skimage.feature import hog


def audio_analysis(video_path, seconds_between_grouped_peaks=1) -> list[tuple[tuple[int, int], float]]:
    audio, sr = librosa.load(video_path)
    rms = librosa.feature.rms(y=audio)[0]

    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    peak_indices = np.where((onset_env > np.mean(onset_env)) & (rms > np.mean(rms)))[0]

    times = librosa.times_like(onset_env, sr=sr)
    t = (seconds_between_grouped_peaks * sr * len(times)) / np.shape(audio)[0]
    clusters = scipy.cluster.hierarchy.fcluster(
        scipy.cluster.hierarchy.linkage(peak_indices[:, None], method='single'),
        t=t, criterion='distance')

    segment_energies = []
    for cluster_id in set(clusters):
        cluster_indices = peak_indices[clusters == cluster_id]
        segment_energy = np.sum(rms[cluster_indices])
        segment_energies.append(((round(times[cluster_indices[0]] * 1000), round(times[cluster_indices[-1]] * 1000)), segment_energy))

    segment_energies.sort(key=lambda x: x[0][0])

    return segment_energies


def text_analysis(wordData: list[dict], shift: int = 3) -> list[tuple[tuple[int, int], float]]:
    data_format: list[tuple[tuple[int, int], float]] = list()
    flagIdx = -1
    for idx in range(len(wordData)):
        if flagIdx == -1 and wordData[idx]["sentiment_analysis"] != 0:
            flagIdx = idx
        if flagIdx != -1 and wordData[idx]["sentiment_analysis"] == 0:
            summ = 0
            for j in range(idx - 1 - flagIdx):
                summ += wordData[flagIdx + j]["sentiment_analysis"]
            data_format.append(((int(wordData[flagIdx]["startTime"]), int(wordData[idx - 1]["endTime"])),
                                summ / (idx - 1 - flagIdx)))
            flagIdx = -1
    return data_format


def extract_frames_from_video(video_path: str, take_every_n_frame=50):
    # Открываем видеофайл
    cap = cv2.VideoCapture(video_path)

    # Проверяем, удалось ли открыть видеофайл
    if not cap.isOpened():
        print(f"Ошибка: не удалось открыть видеофайл {video_path}")
        return []

    frames = []
    c = 0
    while cap.isOpened():
        # Читаем кадр за кадром
        ret, frame = cap.read()
        c += 1
        if not ret:
            break
        # Добавляем кадр в список
        if c % take_every_n_frame == 0: frames.append(frame)

    # Освобождаем захват видео
    cap.release()
    return np.array(frames)


def video_analysis(video_path: str, take_every_n_frame=50, border_of_std=0.1) -> list[tuple[tuple[int, int], float]]:
    frames = extract_frames_from_video(video_path, take_every_n_frame)
    print(f"Извлечено {len(frames)} кадров из видео")

    average_hogs = []
    for i in range(len(frames)):
        # Загрузка изображения
        image = cv2.cvtColor(frames[i],cv2.COLOR_BGR2GRAY)

        #Вычисление HOG
        fd = hog(image, pixels_per_cell=(16, 16), cells_per_block=(4, 4))
        # Вычисление среднего значения HOG дескрипторов
        average_hog_descriptor = np.mean(fd) #выше коэффициент - больше деталей и обьектов в изображении
        average_hogs.append(average_hog_descriptor)

    entropies = []
    for input_image in frames:
        # Загрузка изображения
        image = cv2.cvtColor(input_image,cv2.COLOR_RGB2GRAY)

        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        # Нормализация гистограммы
        hist = hist / np.sum(hist)

        # Вычисление меры энтропии
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        entropies.append(entropy)

    entropies_ = entropies - np.mean(entropies)

    more_detailed_than_usual_frame_indexes = np.where((entropies_ > np.mean(entropies_) + border_of_std * np.std(entropies_)) &
                                                      (average_hogs > np.mean(average_hogs) + border_of_std * np.std(average_hogs)))[0]
    less_detailed_than_usual_frame_indexes = np.where((entropies_ < np.mean(entropies_) - border_of_std * np.std(entropies_)) &
                                                      (average_hogs < np.mean(average_hogs) - border_of_std * np.std(average_hogs)))[0]

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    mspf = 1000/fps #milliseconds per frame

    coef = []
    for ind in list(more_detailed_than_usual_frame_indexes):
        coef.append([(round((abs(int(ind) - 1) * mspf)), round((int(ind) + 1) * mspf)), abs(float(entropies_[ind] + average_hogs[ind]))])

    for ind in list(less_detailed_than_usual_frame_indexes):
        coef.append([(round((abs(int(ind) - 1) * mspf)), round((int(ind) + 1) * mspf)), -1 * abs(float(entropies_[ind] + average_hogs[ind]))])

    coef.sort(key=lambda x: x[0][0])
    return coef