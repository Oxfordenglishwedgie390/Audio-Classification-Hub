"""
pipeline/embedding.py — Step 2: Audio array → 192-dim voice vector
Uses SpeechBrain ECAPA-TDNN pretrained on VoxCeleb.

Windows [WinError 1314] fix:
  SpeechBrain calls  dst.symlink_to(src)  (pathlib.Path method).
  We patch  Path.symlink_to  to fall back to shutil.copy2 on OSError.
  This is the correct intercept point — os.symlink patching does NOT work
  because pathlib in Python 3.13 accesses os.symlink differently.
"""

import shutil
import warnings
import numpy as np
import torch
from pathlib import Path

# ── Patch pathlib.Path.symlink_to BEFORE any SpeechBrain import ──────────────
# SpeechBrain's fetching.py calls:  dst.symlink_to(src)
# On Windows without Developer Mode this raises OSError [WinError 1314].
# We replace the method with one that falls back to shutil.copy2.

_orig_symlink_to = Path.symlink_to

def _safe_symlink_to(self, target, target_is_directory=False):
    try:
        _orig_symlink_to(self, target, target_is_directory)
    except OSError:
        target_p = Path(str(target))
        self.parent.mkdir(parents=True, exist_ok=True)
        if self.is_symlink() or self.exists():
            self.unlink(missing_ok=True)
        shutil.copy2(str(target_p), str(self))

Path.symlink_to = _safe_symlink_to   # global patch — affects all pathlib usage
print("[EMBEDDING] Path.symlink_to patched → fallback to copy on Windows.")

# ─────────────────────────────────────────────────────────────────────────────

_model = None

_SAVE_DIR = Path(__file__).parent.parent / "pretrained_models" / "spkrec-ecapa-voxceleb"
_REPO_ID  = "speechbrain/spkrec-ecapa-voxceleb"


def _ensure_downloaded():
    """Pre-download all model files using HF Hub (no symlinks)."""
    from huggingface_hub import snapshot_download

    print(f"[EMBEDDING] Downloading model to: {_SAVE_DIR}")
    _SAVE_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id=_REPO_ID,
        local_dir=str(_SAVE_DIR),
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "flax_model*", "tf_model*"],
    )
    print(f"[EMBEDDING] Download complete.")


def _load_model():
    global _model
    if _model is not None:
        return _model

    warnings.filterwarnings("ignore", message=".*SYMLINK.*", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*symlink.*", category=UserWarning)

    # Download if not already cached
    if not (_SAVE_DIR / "hyperparams.yaml").exists():
        _ensure_downloaded()
    else:
        print(f"[EMBEDDING] Using cached model at: {_SAVE_DIR}")

    try:
        from speechbrain.inference.classifiers import EncoderClassifier
    except ImportError:
        from speechbrain.pretrained import EncoderClassifier

    # Even with a local source, SpeechBrain's pretrainer.collect_files()
    # may still try to fetch/link files. Our Path.symlink_to patch handles it.
    _model = EncoderClassifier.from_hparams(
        source=str(_SAVE_DIR),
        savedir=str(_SAVE_DIR),
        run_opts={"device": "cpu"},
    )

    print("[EMBEDDING] ECAPA-TDNN loaded successfully.")
    return _model


def get_embedding(audio: np.ndarray) -> np.ndarray:
    """
    Input : numpy float32 array (N,) at 16kHz
    Output: numpy float32 array (192,) — the voice fingerprint
    """
    model = _load_model()
    tensor = torch.FloatTensor(audio).unsqueeze(0)
    with torch.no_grad():
        emb = model.encode_batch(tensor)
    return emb.squeeze().numpy().astype(np.float32)
