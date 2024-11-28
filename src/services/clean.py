from typing import List
from datetime import timedelta
from aiofiles import os
import asyncio

from sqlalchemy import Result

from services.interfaces import ICleanDisk
from models.file import File
from utils.asyncio import gather_with_concurrency
from utils.time import get_current_time
from utils.repo import IRepo


class CleanDisk(ICleanDisk):
    def __init__(self, max_days: int, max_days_unused: int, repo: IRepo[File]):
        self.max_days = max_days
        self.max_days_unused = max_days_unused
        self.repo = repo

    async def __call__(self) -> None:
        tasks = []
        for file in await self.repo.get_by_filters(
            filters={
                "created_at": get_current_time() - timedelta(days=self.max_days),
                # "updated_at": get_current_time() - timedelta(days=self.max_days_unused),
                "is_removed_from_disk": False,
            },
            operator_overrides={
                "created_at": "le",
                "updated_at": "le",
                "is_removed_from_disk": "is",
            },
        ):
            tasks.append(asyncio.Task(self._delete_from_disk(file[0])))

        print(tasks)
        result = await gather_with_concurrency(tasks)
        print(result)
        if result:
            await self._update_in_db(list(uuid for uuid in result if uuid is not None))

    async def _get_files_for_cleanup(self) -> Result[File]:
        return await self.repo.get_by_filters(
            filters={
                "created_at": get_current_time() - timedelta(days=self.max_days),
                "updated_at": get_current_time() - timedelta(days=self.max_days_unused),
                "is_removed_from_disk": False,
            },
            operator_overrides={
                "created_at": "le",
                "updated_at": "le",
                "is_removed_from_disk": "is",
            },
        )

    async def _delete_from_disk(self, file: File) -> str | None:
        try:
            await os.remove(file.path)
            return file.uuid
        except FileNotFoundError as e:
            # TODO: Logging
            return None

    async def _update_in_db(self, uuids: List[str]) -> None:
        await self.repo.multi_update(uuids, values={"is_removed_from_disk": True})
