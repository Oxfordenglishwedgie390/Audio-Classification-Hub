import numpy as np
import librosa
from .exceptions import AudioFileNotFoundError, AudioTooShortError

SR       = 16000
DURATION = 3
MIN_SEC  = 2.0


def clean_audio(file_path: str) -> np.ndarray:
    try:
        y, sr = librosa.load(file_path, sr=SR, mono=True)
    except Exception as e:
        raise AudioFileNotFoundError(f"Cannot read: {file_path} — {e}")

    if len(y) / SR < MIN_SEC:
        raise AudioTooShortError(f"Audio too short. Minimum {MIN_SEC}s required.")

    target = SR * DURATION
    if len(y) < target:
        y = np.pad(y, (0, target - len(y)))
    else:
        y = y[:target]

    peak = np.abs(y).max()
    if peak > 0:
        y = y / peak

    return y.astype(np.float32)
