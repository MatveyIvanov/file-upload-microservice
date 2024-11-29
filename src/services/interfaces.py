from __future__ import annotations

from abc import ABC, abstractmethod

from boto3 import Session
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models.file import File
from schemas.files import FileMetadata, UploadedFile
from utils.repo import IRepo
from utils.sqlalchemy import IFilter


class ICreateFile(ABC):
    @abstractmethod
    def __init__(
        self,
        base_path: str,
        repo: IRepo[File],
        extract_metadata: IExtractMetadata,
    ) -> None:
        """
        :param base_path: base path for all files
        :type base_path: str
        :param repo: file repository
        :type repo: IRepo[File]
        :param extract_metadata: metadata extractor
        :type extract_metadata: IExtractMetadata
        """
        ...

    @abstractmethod
    async def __call__(
        self,
        file: UploadFile,
        *,
        session: AsyncSession = None,
    ) -> UploadedFile:
        """
        :param file: file to create
        :type file: UploadFile
        :param session: database session, defaults to None
        :type session: AsyncSession, optional
        :return: uploaded file data
        :rtype: UploadedFile
        """
        ...


class IExtractMetadata(ABC):
    @abstractmethod
    def __call__(self, file: UploadFile) -> FileMetadata:
        """
        :param file: upload file object with binary and metadata
        :type file: UploadFile
        :return: file metadata
        :rtype: FileMetadata
        """
        ...


class ISaveFileToExternalStorage(ABC):
    @abstractmethod
    def __init__(
        self,
        repo: IRepo[File],
        boto3: Session,
        endpoint_url: str,
        bucket: str,
    ) -> None:
        """
        :param repo: file repository
        :type repo: IRepo[File]
        :param boto3: boto3 initialized session
        :type boto3: Session
        :param endpoint_url: bucket endpoint url
        :type endpoint_url: str
        :param bucket: bucket name
        :type bucket: str
        """
        ...

    @abstractmethod
    async def __call__(self, uuid: str) -> None:
        """
        :param uuid: uuid of a file
        :type uuid: str
        """
        ...


class ICleanDisk(ABC):
    @abstractmethod
    def __init__(
        self,
        max_days: int,
        max_days_unused: int,
        repo: IRepo[File],
        created_at_filter: IFilter[File],
        updated_at_filter: IFilter[File],
        is_removed_from_disk_filter: IFilter[File],
    ) -> None:
        """
        :param max_days: max number of days that
            file can be keeped on disk after creation
        :type max_days: int
        :param max_days_unused: max number of days
            that file can be keeped on disk after last update
        :type max_days_unused: int
        :param repo: file repository
        :type repo: IRepo[File]
        :param created_at_filter: _description_
        :type created_at_filter: IFilter[File]
        :param updated_at_filter: _description_
        :type updated_at_filter: IFilter[File]
        :param is_removed_from_disk_filter: _description_
        :type is_removed_from_disk_filter: IFilter[File]
        """
        ...

    @abstractmethod
    async def __call__(self) -> None: ...
