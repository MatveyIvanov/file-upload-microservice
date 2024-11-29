from typing import AsyncGenerator
import aiofiles


async def chunk_file(path: str, *, chunk_size: int = 1024) -> AsyncGenerator:
    """
    Read file from disk in chunks

    :param path: path to the file
    :type path: str
    :param chunk_size: chunk size in bytes, defaults to 1024
    :type chunk_size: int, optional
    :return: async generator
    :rtype: AsyncGenerator
    :yield: chunk bytes
    :rtype: Iterator[AsyncGenerator]
    """
    async with aiofiles.open(path, "rb") as f:
        while chunk := await f.read(chunk_size):
            yield chunk
