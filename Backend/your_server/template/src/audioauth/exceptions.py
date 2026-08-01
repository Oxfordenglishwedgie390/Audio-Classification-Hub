class AudioAuthError(Exception):
    pass

class AudioTooShortError(AudioAuthError):
    pass

class AudioFileNotFoundError(AudioAuthError):
    pass
