from abc import ABC, abstractmethod

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.files import FileMetadata, UploadedFile


class ICreateFile(ABC):
    @abstractmethod
    async def __call__(
        self,
        file: UploadFile,
        *,
        session: AsyncSession = None,
    ) -> UploadedFile: ...


class IExtractMetadata(ABC):
    @abstractmethod
    def __call__(self, file: UploadFile) -> FileMetadata: ...
