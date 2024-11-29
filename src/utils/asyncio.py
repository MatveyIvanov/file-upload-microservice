import asyncio
from typing import List, TypeVar

DEFAULT_CONCURRENCY: int = 5


TResult = TypeVar("TResult")


async def gather_with_concurrency(
    tasks: List[asyncio.Task[TResult]],
    *,
    max_concurrency: int = DEFAULT_CONCURRENCY,
) -> List[TResult]:
    """
    Function that allows to do asyncio.gather
    with specified concurrency

    :param tasks: list of asyncio tasks
    :type tasks: List[asyncio.Task[TResult]]
    :param max_concurrency: max concurrency, defaults to DEFAULT_CONCURRENCY
    :type max_concurrency: int, optional
    :return: list with gather results
    :rtype: List[TResult]
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def semaphore_task(task: asyncio.Task[TResult]) -> TResult:
        async with semaphore:
            return await task

    return await asyncio.gather(*(semaphore_task(task) for task in tasks))
