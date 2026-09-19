import boto3

from app.storage.base import FileStorage


class S3FileStorage(FileStorage):
    """Works with AWS S3 or any S3-compatible object store (Cloudflare R2,
    Backblaze B2, MinIO) by pointing `endpoint_url` at it. Resumes contain
    personal data, so objects are written private by default -- there is no
    public-read ACL here even when `public_base_url` is set for a CDN in
    front of the bucket.
    """

    def __init__(
        self,
        bucket: str,
        region: str,
        access_key_id: str,
        secret_access_key: str,
        endpoint_url: str = "",
        public_base_url: str = "",
    ):
        self._bucket = bucket
        self._public_base_url = public_base_url.rstrip("/")
        self._client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
            endpoint_url=endpoint_url or None,
        )

    def save(self, key: str, content: bytes, content_type: str) -> str:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=content, ContentType=content_type)
        if self._public_base_url:
            return f"{self._public_base_url}/{key}"
        return f"s3://{self._bucket}/{key}"
