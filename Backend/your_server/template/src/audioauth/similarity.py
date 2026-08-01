import numpy as np

THRESHOLD_STRONG  = 0.75
THRESHOLD_PARTIAL = 0.60


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot   = np.dot(vec1, vec2)
    norms = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return float(dot / norms) if norms > 0 else 0.0


def decide(score: float) -> tuple:
    if score >= THRESHOLD_STRONG:
        return True, "STRONG MATCH"
    elif score >= THRESHOLD_PARTIAL:
        return True, "PARTIAL MATCH"
    return False, "REJECTED"
