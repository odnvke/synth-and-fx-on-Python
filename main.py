import numpy as np
import wavio
import os
from mainSynth import *
#from func import *

# ---------- параметры из settings ----------
RATE        = 44100
DURATION    = 12
STEREO      = 1
OUT_NAME    = "out.wav"
SYNTH_OR_FX = False
INP_NAME    = "inp.wav"
# -----------------------------------------

def load_wav(path: str) -> np.ndarray:
    """Возвращает нормализованный к [-1..1] float32 массив."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"fail {path} ne naiden")

    wav = wavio.read(path)
    data = wav.data.astype(np.float32)

    # нормализация к [-1..1]
    if wav.sampwidth == 1:          # 8-бит unsigned
        data = (data - 128) / 128.0
    elif wav.sampwidth == 2:        # 16-бит signed
        data /= 32768.0
    elif wav.sampwidth == 3:        # 24-бит signed
        data /= 8388608.0
    elif wav.sampwidth == 4:        # 32-бит signed
        data /= 2147483648.0
    else:
        raise ValueError("neizvestnui format bitnosti")

    # приведение к моно/стерео
    if len(data.shape) == 1:
        if STEREO:
            data = np.column_stack([data, data])
    else:
        if data.shape[1] == 1:
            data = data[:, 0]
            if STEREO != 0:
                data = np.column_stack([data, data])
        else:
            if STEREO == 0:
                data = data.mean(axis=1)
    return data

def save_wav(path: str, data: np.ndarray, sr: int = RATE):
    """Сохраняет float32 массив в 24-бит WAV."""
    # убедимся, что данные в [-1..1]
    data = np.clip(data, -1.0, 1.0)
    # перевод в 24-бит signed integer
    data_24 = (data * 8388607).astype(np.int32)
    wavio.write(path, data_24, sr, sampwidth=3)

# ------------------------------------------------------------------

length = int(DURATION * RATE)
if STEREO != 0:
    out = np.zeros((length, 2), dtype=np.float32)
else:
    out = np.zeros((length, 1), dtype=np.float32)

if SYNTH_OR_FX:
    # синтез
    track = np.array([["3C"], ["3E"]])
    track = setup(track)
    for i in range(length):
        idx = int((i / length) * track.size)
        smp = sinth(track[idx])
        if STEREO != 0:
            out[i, 0] = smp[0]
            out[i, 1] = smp[1]
        else:
            out[i, 0] = smp[0] if isinstance(smp, tuple) else smp
else:
    # эффект
    inp = load_wav(INP_NAME)
    if STEREO == 1:
        for i in range(length):
            out[i, 0], out[i, 1] = fx(inp[i, 0], inp[i, 1])
    elif STEREO == 2:
        for i in range(length):
            out[i, 0], out[i, 1] = fx(inp[i, 0]), fx(inp[i, 1])
            
    else:
        for i in range(length):
            out[i, 0] = fx(inp[i, 0])

save_wav(OUT_NAME, out)
print(f"Сохранено: {OUT_NAME}")