from dependency_injector import containers, providers

from config import settings
from config.db import Database
from services import *
from models.file import File
from utils.repo import Repo


class Container(containers.DeclarativeContainer):
    db = providers.Resource(Database, db_url=settings.DATABASE_URL)

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
