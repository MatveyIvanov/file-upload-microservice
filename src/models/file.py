from datetime import datetime
from sqlalchemy import (
    Table,
    Column,
    String,
    DateTime,
    func,
    UUID,
    BigInteger,
)
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
    uuid: str
    path: str
    size: int
    format: str
    name: str
    ext: str
    created_at: datetime
    updated_at: datetime


file_mapper = mapper_registry.map_imperatively(File, file_table)
