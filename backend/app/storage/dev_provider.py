from pathlib import Path

from app.storage.base import FileStorage

_STORAGE_ROOT = Path(__file__).resolve().parents[2] / "var" / "uploads"


class DevFileStorage(FileStorage):
    """Local disk storage for development.

    Not suitable for most PaaS deployments: their filesystems are ephemeral
    (wiped on every redeploy/restart) or read-only. Use S3FileStorage there.
    """

    def save(self, key: str, content: bytes, content_type: str) -> str:
        path = _STORAGE_ROOT / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)
