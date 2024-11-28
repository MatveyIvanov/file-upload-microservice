import asyncio
from typing import List, TypeVar

DEFAULT_CONCURRENCY: int = 5


TResult = TypeVar("TResult")


async def gather_with_concurrency(
    tasks: List[asyncio.Task[TResult]],
    *,
    max_concurrency: int = DEFAULT_CONCURRENCY,
) -> List[TResult]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async def semaphore_task(task: asyncio.Task[TResult]) -> TResult:
        async with semaphore:
            return await task

    return await asyncio.gather(*(semaphore_task(task) for task in tasks))
