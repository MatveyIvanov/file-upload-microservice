import logging

import aiofiles
from aioboto3 import Session

from models.file import File
from services.interfaces import ISaveFileToExternalStorage
from utils.repo import IRepo

logger = logging.getLogger("s3")


class SaveFileToS3(ISaveFileToExternalStorage):
    def __init__(
        self,
        repo: IRepo[File],
        boto3: Session,
        endpoint_url: str,
        bucket: str,
    ) -> None:
        self.repo = repo
        self.boto3 = boto3
        self.endpoint_url = endpoint_url
        self.bucket = bucket

    async def __call__(self, uuid: str) -> bool:
        file = await self._get_file(uuid)
        sent = await self._save_to_s3(file)
        if sent:
            await self._update_file(file)
        return sent

    async def _get_file(self, uuid: str) -> File:
        return await self.repo.get_by_id(uuid)

    async def _save_to_s3(self, file: File) -> bool:
        try:
            async with self.boto3.client("s3", endpoint_url=self.endpoint_url) as s3:
                async with aiofiles.open(file.path, "rb") as stream:
                    await s3.upload_fileobj(
                        stream,
                        self.bucket,
                        file.path.strip("/"),
                    )
            return True
        except Exception as e:
            logger.critical(
                f"Error saving a file to s3. - {str(e)}",
                extra={"uuid": file.uuid, "path": file.path},
            )
            return False

    async def _update_file(self, file: File) -> None:
        await self.repo.update(file, values={"is_saved_to_s3": True})
