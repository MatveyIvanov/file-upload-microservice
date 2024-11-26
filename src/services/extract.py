from fastapi import UploadFile

from services.interfaces import IExtractMetadata
from schemas.files import FileMetadata


class ExtractMetadata(IExtractMetadata):
    def __call__(self, file: UploadFile) -> FileMetadata:
        return FileMetadata(
            size=file.size,
            format=file.headers.get("content-type", "unknown"),
            name=file.filename,
            ext=file.filename.split(".")[-1],
        )
