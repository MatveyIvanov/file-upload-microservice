from datetime import datetime

from pydantic import UUID4, BaseModel


class UploadedFile(BaseModel):
    uuid: UUID4
    path: str
    size: int
    format: str
    name: str
    ext: str
    created_at: datetime
    available_for_download: bool


class CreateFileSchema(BaseModel):
    uuid: UUID4
    path: str
    size: int
    format: str
    name: str
    ext: str


class FileMetadata(BaseModel):
    size: int
    format: str
    name: str
    ext: str
