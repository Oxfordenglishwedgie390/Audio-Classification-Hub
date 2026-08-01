"""
pipeline/preprocess.py — Step 1: Clean uploaded audio
Input  : file path (str)
Output : numpy float32 array, 16kHz mono, padded/trimmed to DURATION seconds

Supports: .wav  .mp3  .flac  .ogg  .webm  .mp4 .m4a  (browser-recorded formats)
Strategy: Try torchaudio first (handles webm/ogg natively), fall back to librosa.
"""

import os
import numpy as np

SR          = 16000   # ECAPA-TDNN requires 16kHz
DURATION    = 3       # seconds used for embedding (first N seconds)
MIN_SEC     = 2.0     # reject audio shorter than this


# ── Try torchaudio backend first ─────────────────────────────────────────────
def _load_with_torchaudio(file_path: str):
    import torchaudio
    import torchaudio.transforms as T

    # Try soundfile backend (fast, no ffmpeg needed for wav/flac/ogg)
    for backend in ("soundfile", "sox_io", None):
        try:
            if backend:
                torchaudio.set_audio_backend(backend)
            waveform, sr = torchaudio.load(file_path)   # (C, T)
            break
        except Exception:
            continue
    else:
        raise RuntimeError("torchaudio could not load the file with any backend")

    # Resample if needed
    if sr != SR:
        resampler = T.Resample(orig_freq=sr, new_freq=SR)
        waveform  = resampler(waveform)

    # Mix down to mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    return waveform.squeeze(0).numpy().astype(np.float32)   # (T,)


# ── Fall back to librosa (needs ffmpeg for webm/mp4) ────────────────────────
def _load_with_librosa(file_path: str):
    import librosa
    y, _ = librosa.load(file_path, sr=SR, mono=True)
    return y.astype(np.float32)


# ── Try soundfile directly (wav/flac/ogg) ────────────────────────────────────
def _load_with_soundfile(file_path: str):
    import soundfile as sf
    import resampy

    data, sr = sf.read(file_path, dtype="float32", always_2d=True)
    data = data.mean(axis=1)     # mono

    if sr != SR:
        data = resampy.resample(data, sr, SR)

    return data.astype(np.float32)


def _load_audio_raw(file_path: str) -> np.ndarray:
    """
    Try multiple backends in order of preference.
    Returns raw float32 array at SR Hz.
    """
    errors = []

    # 1. torchaudio — best for browser-recorded webm/ogg/wav
    try:
        return _load_with_torchaudio(file_path)
    except Exception as e:
        errors.append(f"torchaudio: {e}")

    # 2. soundfile — fast for wav/flac/ogg (no ffmpeg)
    try:
        return _load_with_soundfile(file_path)
    except Exception as e:
        errors.append(f"soundfile: {e}")

    # 3. librosa — final fallback (needs ffmpeg for webm/mp4)
    try:
        return _load_with_librosa(file_path)
    except Exception as e:
        errors.append(f"librosa: {e}")

    ext = os.path.splitext(file_path)[-1].lower()
    raise ValueError(
        f"Cannot read audio file (ext={ext}). "
        f"If the file is .webm or .mp4, install ffmpeg and add it to PATH. "
        f"Errors: {' | '.join(errors)}"
    )


def clean_audio(file_path: str) -> np.ndarray:
    """
    Load any audio file and return a clean, normalised float32 array at 16kHz.
    Handles browser-recorded webm/ogg/mp4 formats without requiring ffmpeg.
    """
    y = _load_audio_raw(file_path)

    # Reject files that are too short
    duration = len(y) / SR
    if duration < MIN_SEC:
        raise ValueError(
            f"Audio is {duration:.2f}s — too short (minimum {MIN_SEC}s). "
            f"Please speak for at least {MIN_SEC} second(s)."
        )

    # Pad with silence or trim to exactly DURATION seconds
    target = SR * DURATION
    if len(y) < target:
        y = np.pad(y, (0, target - len(y)))
    else:
        y = y[:target]

    # Peak normalise to [-1, 1]
    peak = np.abs(y).max()
    if peak > 1e-6:
        y = y / peak

    return y.astype(np.float32)
