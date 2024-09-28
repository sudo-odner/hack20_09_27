import librosa
import numpy as np
import scipy


def audio_analysis(video_path, seconds_between_grouped_peaks = 1) -> list[tuple[tuple[int, int], float]]:
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
        segment_energies.append(((round(times[cluster_indices[0]] * sr),round(times[cluster_indices[-1]] * sr)), segment_energy))

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


def video_analysis():
    pass