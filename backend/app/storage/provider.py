from functools import lru_cache

from app.core.config import get_settings
from app.storage.base import FileStorage
from app.storage.dev_provider import DevFileStorage


class NoFileStorage(FileStorage):
    """Doesn't keep uploaded files at all.

    The resume is parsed in memory and only the extracted, user-approved
    fields are saved -- the right default for serverless hosts with no
    writable disk, and the most privacy-friendly option.
    """

    def save(self, key: str, content: bytes, content_type: str) -> str:
        return ""


@lru_cache
def get_file_storage() -> FileStorage:
    settings = get_settings()
    if settings.storage_provider == "none":
        return NoFileStorage()
    if settings.storage_provider == "s3":
        from app.storage.s3_provider import S3FileStorage

        return S3FileStorage(
            bucket=settings.storage_bucket,
            region=settings.storage_region,
            access_key_id=settings.storage_access_key_id,
            secret_access_key=settings.storage_secret_access_key,
            endpoint_url=settings.storage_endpoint_url,
            public_base_url=settings.storage_public_base_url,
        )
    return DevFileStorage()
