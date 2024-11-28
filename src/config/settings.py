import os

DB_USER: str = os.environ.get("DB_USER", "")
DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
DB_NAME: str = os.environ.get("DB_NAME", "")
DB_HOST: str = os.environ.get("DB_HOST", "")
DB_PORT: str = os.environ.get("DB_PORT", "")
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

TIMEZONE = os.environ.get("TIMEZONE", "UTC")

DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROD = bool(int(os.environ.get("PROD", 1)))

LOGGING_MAX_BYTES = int(os.environ.get("LOGGING_MAX_BYTES", 1024 * 3))
LOGGING_BACKUP_COUNT = int(os.environ.get("LOGGING_BACKUP_COUNT", 1))
LOGGING_LOGGERS = os.environ.get("LOGGING_LOGGERS", "").split(",")
LOGGING_SENSITIVE_FIELDS = os.environ.get("LOGGING_SENSITIVE_FIELDS", "").split(",")
LOGGING_PATH = os.environ.get("LOG_PATH")

PORT = os.environ.get("ASGI_PORT")

UPLOAD_MAX_SIZE_IN_BYTES: int = int(
    os.environ.get(
        "UPLOAD_MAX_SIZE_IN_BYTES",
        100 * 1024 * 1024,
    )
)

MEDIA_ROOT: str = "/media"

# S3
AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_SESSION_TOKEN: str = os.environ.get("AWS_SESSION_TOKEN", "")
AWS_ENDPOINT_URL: str = os.environ.get("AWS_ENDPOINT_URL", "")
AWS_REGION_NAME: str = os.environ.get("AWS_REGION_NAME", "")
AWS_BUCKET_NAME: str = os.environ.get("AWS_BUCKET_NAME", "")

# Scheduler
SCHEDULER_DISK_CLEANUP_EVERY: int = int(
    os.environ.get(
        "SCHEDULER_DISK_CLEANUP_EVERY",
        3600,
    )
)  # in minutes
SCHEDULER_REMOVE_FILES_OLDER_THAN: int = int(
    os.environ.get(
        "SCHEDULER_REMOVE_FILES_OLDER_THAN",
        30,
    )
)  # in days
SCHEDULER_REMOVE_FILES_UNUSED_MORE_THAN: int = int(
    os.environ.get(
        "SCHEDULER_REMOVE_FILES_UNUSED_MORE_THAN",
        30,
    )
)  # in days
