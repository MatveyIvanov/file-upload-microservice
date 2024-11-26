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
    updated_at: datetime


class FileMetadata(BaseModel):
    size: int
    format: str
    name: str
    ext: str
