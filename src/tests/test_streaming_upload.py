from io import BufferedReader

import httpx


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
        # upload = FileLimiter(file, 128)
        response = httpx.post(
            "http://localhost:8000/api/v0/uploads/file/stream/",
            files={"file": file},
            headers={
                "Content-Type": "application/octet-stream",
                "filename": "file.png",
            },
        )
        print(response.content.decode())


if __name__ == "__main__":
    upload()
