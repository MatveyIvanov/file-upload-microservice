import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.file import File
from schemas.files import CreateFileSchema, FileMetadata, UploadedFile
from services.interfaces import ICreateFile, IExtractMetadata
from utils.decorators import session
from utils.exceptions import Custom400Exception
from utils.random import random_string
from utils.repo import IRepo


class CreateFile(ICreateFile):
    def __init__(
        self,
        base_path: str,
        repo: IRepo[File],
        extract_metadata: IExtractMetadata,
    ) -> None:
        self.base_path = base_path
        self.repo = repo
        self.extract_metadata = extract_metadata

    @session
    async def __call__(
        self,
        file: UploadFile,
        *,
        session: AsyncSession = None,
    ) -> UploadedFile:
        metadata = self._extract_metadata(file)
        self._validate_metadata(metadata)
        path = await self._save_to_disk(file, metadata)
        instance = await self._create(path, metadata, session)
        return UploadedFile(
            uuid=instance.uuid,
            path=instance.path,
            size=instance.size,
            format=instance.format,
            name=instance.name,
            ext=instance.ext,
            created_at=instance.created_at,
            available_for_download=instance.is_removed_from_disk is False,
        )

    def _extract_metadata(self, file: UploadFile) -> FileMetadata:
        return self.extract_metadata(file)

    def _validate_metadata(self, metadata: FileMetadata) -> None:
        if metadata.size > settings.UPLOAD_MAX_SIZE_IN_BYTES:
            raise Custom400Exception("Размер файла превышает лимит.")

    async def _save_to_disk(self, file: UploadFile, metadata: FileMetadata) -> str:
        path = str(Path(self.base_path, f"{random_string()}.{metadata.ext}"))
        async with aiofiles.open(path, "wb") as stream:
            await stream.write(file.file.read())
        return path

    async def _create(
        self,
        path: str,
        metadata: FileMetadata,
        session: AsyncSession,
    ) -> File:
        return await self.repo.create(
            entry=CreateFileSchema(
                uuid=str(uuid.uuid4()),
                path=path,
                size=metadata.size,
                format=metadata.format,
                name=metadata.name,
                ext=metadata.ext,
            ),
            session=session,
        )
