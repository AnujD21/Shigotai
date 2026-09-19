from abc import ABC, abstractmethod


class FileStorage(ABC):
    """Where uploaded files (currently: resumes) actually live.

    `save` returns an opaque reference string that this same implementation
    can later resolve -- callers (e.g. the resume endpoint) just persist
    whatever string comes back, they never need to know if it's a local path
    or an object-store key.
    """

    @abstractmethod
    def save(self, key: str, content: bytes, content_type: str) -> str: ...
