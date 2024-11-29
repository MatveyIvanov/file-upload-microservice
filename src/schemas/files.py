from datetime import datetime

from pydantic import UUID4, BaseModel


class UploadedFile(BaseModel):
    """Schema for uploaded file representation"""

    uuid: UUID4
    path: str
    size: int
    format: str
    name: str
    ext: str
    created_at: datetime
    available_for_download: bool


class CreateFileSchema(BaseModel):
    """Schema for file creation"""

    uuid: UUID4
    path: str
    size: int
    format: str
    name: str
    ext: str


class FileMetadata(BaseModel):
    """Schema for file metadata"""

    size: int
    format: str
    name: str
    ext: str
