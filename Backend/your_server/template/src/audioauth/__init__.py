from .core import authenticate, authenticate_with_score
from .exceptions import (
    AudioAuthError,
    AudioTooShortError,
    AudioFileNotFoundError,
)

__all__ = [
    "authenticate",
    "authenticate_with_score",
    "AudioAuthError",
    "AudioTooShortError",
    "AudioFileNotFoundError",
]

__version__ = "1.0.0"
