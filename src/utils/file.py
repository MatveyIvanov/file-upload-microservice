from typing import AsyncGenerator
import aiofiles


async def chunk_file(path: str, *, chunk_size: int = 1024) -> AsyncGenerator:
    async with aiofiles.open(path, "rb") as f:
        while chunk := await f.read(chunk_size):
            yield chunk
