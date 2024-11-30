import asyncio
import logging
from datetime import timedelta
from typing import List

from aiofiles import os
from sqlalchemy import Result

from models.file import File
from services.interfaces import ICleanDisk
from utils.asyncio import gather_with_concurrency
from utils.repo import IRepo
from utils.sqlalchemy import IFilter, IFilterSeq, mode, operator
from utils.time import get_current_time

logger = logging.getLogger("cleanup")


class CleanDisk(ICleanDisk):
    def __init__(
        self,
        max_days: int,
        max_days_unused: int,
        repo: IRepo[File],
        created_at_filter: IFilter[File],
        updated_at_filter: IFilter[File],
        is_removed_from_disk_filter: IFilter[File],
        filter_seq_class: IFilterSeq,
    ) -> None:
        self.max_days = max_days
        self.max_days_unused = max_days_unused
        self.repo = repo
        self.created_at_filter = created_at_filter
        self.updated_at_filter = updated_at_filter
        self.is_removed_from_disk_filter = is_removed_from_disk_filter
        self.filter_seq_class = filter_seq_class

    async def __call__(self) -> None:
        tasks: List[asyncio.Task[str | None]] = []
        for file in await self._get_files_for_cleanup():
            tasks.append(asyncio.Task(self._delete_from_disk(file[0])))

        # no need to do it in specific order synchronously,
        # just gather and get all results
        result = await gather_with_concurrency(tasks)
        if result:
            await self._update_in_db(list(uuid for uuid in result if uuid is not None))

    async def _get_files_for_cleanup(self) -> Result[File]:
        return await self.repo.get_by_filters(
            filters=self.filter_seq_class(
                mode.and_,
                self.is_removed_from_disk_filter(False, operator.is_),
                self.filter_seq_class(
                    mode.or_,
                    self.created_at_filter(
                        get_current_time() - timedelta(days=self.max_days), operator.le
                    ),
                    self.updated_at_filter(
                        get_current_time() - timedelta(days=self.max_days_unused),
                        operator.le,
                    ),
                ),
            )
        )

    async def _delete_from_disk(self, file: File) -> str | None:
        try:
            await os.remove(file.path)
            return file.uuid
        except FileNotFoundError:
            logger.error(
                "Error cleaning disk from file.",
                extra={"uuid": file.uuid, "path": file.path},
            )
            return None

    async def _update_in_db(self, uuids: List[str]) -> None:
        await self.repo.multi_update(uuids, values={"is_removed_from_disk": True})
