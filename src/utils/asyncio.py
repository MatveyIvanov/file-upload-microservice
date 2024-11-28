import asyncio
from typing import List, Any

DEFAULT_CONCURRENCY: int = 5


async def gather_with_concurrency(
    tasks: List[asyncio.Task],
    *,
    max_concurrency: int = DEFAULT_CONCURRENCY,
) -> asyncio.Future:
    semaphore = asyncio.Semaphore(max_concurrency)

    async def semaphore_task(task: asyncio.Task) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(semaphore_task(task) for task in tasks))
