from django.contrib.staticfiles.storage import ManifestFilesMixin
from storages.backends.s3 import S3Storage


class ManifestS3Storage(ManifestFilesMixin, S3Storage):
    """S3 storage backend that appends content hashes to filenames.

    This ensures CDN caches (like Cloudflare) serve updated files
    after each deploy, since the filename changes when content changes.
    """
    pass
