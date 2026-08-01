"""
pipeline/averaging.py — Step 3: Average multiple embeddings → master voice
Input  : list of (192,) numpy arrays — one per uploaded file
Output : single (192,) numpy array — the user's master voice fingerprint
"""

import numpy as np


def build_master(embeddings: list) -> np.ndarray:
    """
    Stack all per-file embeddings and compute the mean.
    The result is the user's unique voice identity vector.

    More files uploaded = more accurate and robust master embedding.

    Input : list of numpy arrays, each shape (192,)
    Output: numpy array shape (192,)
    """
    if not embeddings:
        raise ValueError("No embeddings provided — cannot build master voice.")

    stacked = np.stack(embeddings, axis=0)   # shape (N, 192)
    master  = np.mean(stacked, axis=0)       # shape (192,)

    return master.astype(np.float32)
