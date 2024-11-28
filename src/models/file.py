from datetime import datetime
from uuid import UUID as UUIDType

from sqlalchemy import UUID, BigInteger, Boolean, Column, DateTime, String, Table, func
from sqlalchemy.orm import registry

mapper_registry = registry()


file_table = Table(
    "files",
    mapper_registry.metadata,
    Column(
        "uuid",
        UUID,
        primary_key=True,
        unique=True,
        nullable=False,
    ),
    Column("path", String(250), nullable=False),
    Column("size", BigInteger, nullable=False),
    Column("format", String(64), nullable=False),
    Column("name", String(256), nullable=False),
    Column("ext", String(16), nullable=True),
    Column("is_saved_to_s3", Boolean, default=False, nullable=False),
    Column("is_removed_from_disk", Boolean, default=False, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
)


class File:
    uuid: UUIDType
    path: str
    size: int
    format: str
    name: str
    ext: str
    is_saved_to_s3: bool
    is_removed_from_disk: bool
    created_at: datetime
    updated_at: datetime


file_mapper = mapper_registry.map_imperatively(File, file_table)
