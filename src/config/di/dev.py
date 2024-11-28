import aioboto3
from dependency_injector import containers, providers

from config import settings
from config.db import Database
from services import *
from models.file import File
from utils.repo import Repo


class Container(containers.DeclarativeContainer):
    db = providers.Resource(Database, db_url=settings.DATABASE_URL)

    boto3 = providers.Object(
        aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION_NAME,
        )
    )

    file_repo = providers.Singleton(
        Repo[File],
        db=db,
        model_class=File,
        pk_field="uuid",
    )

    extract_metadata = providers.Singleton(ExtractMetadata)
    create_file = providers.Singleton(
        CreateFile,
        base_path=settings.MEDIA_ROOT,
        repo=file_repo,
        extract_metadata=extract_metadata,
    )
    save_file_to_s3 = providers.Singleton(
        SaveFileToS3,
        repo=file_repo,
        boto3=boto3,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        bucket=settings.AWS_BUCKET_NAME,
    )
    clean_disk = providers.Singleton(
        CleanDisk,
        max_days=settings.SCHEDULER_REMOVE_FILES_OLDER_THAN,
        max_days_unused=settings.SCHEDULER_REMOVE_FILES_UNUSED_MORE_THAN,
        repo=file_repo,
    )
