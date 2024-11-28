from io import BufferedReader
from config import settings

import requests


class FileLimiter:
    def __init__(self, file: BufferedReader, chunk_size: int):
        self.chunk_size = chunk_size
        self.file = file
        self.finished = False

    def read(self, amount=-1):
        if self.finished:
            return b""
        data = self.file.read(self.chunk_size)
        if data == b"":
            self.finished = True
        return data


def upload():
    with open("/media/XTXZRMLBFBIIDDINESHX.png", "rb") as file:
        upload = FileLimiter(file, 128)
        response = requests.post(
            f"http://localhost:{settings.PORT}/api/v0/uploads/file/stream/",
            data=upload,
            headers={
                "Content-Type": "application/octet-stream",
                "filename": "file.png",
            },
        )
        print(response.content.decode())


if __name__ == "__main__":
    upload()
