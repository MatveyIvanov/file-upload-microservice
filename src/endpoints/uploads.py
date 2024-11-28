import io
from typing import Annotated
from urllib.parse import unquote
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Header, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi_versioning import version

from config.di import Container
from schemas.files import UploadedFile
from services.interfaces import ICreateFile
from models.file import File
from utils.file import chunk_file
from utils.repo import IRepo
from utils.routing import APIRouter


router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/file/", response_model=UploadedFile)
@version(0)
@inject
async def upload_file(
    file: UploadFile,
    create_file: ICreateFile = Depends(Provide[Container.create_file]),
):
    return await create_file(file)


@router.post("/file/stream/", response_model=UploadedFile)
@version(0)
@inject
async def stream_upload_file(
    request: Request,
    filename: Annotated[str, Header()],
    content_type: Annotated[str, Header(regex=r"application/octet-stream")],
    create_file: ICreateFile = Depends(Provide[Container.create_file]),
):
    buffer = io.BytesIO()
    async for chunk in request.stream():
        buffer.write(chunk)

    buffer.seek(0)
    return await create_file(
        file=UploadFile(
            file=buffer,
            size=buffer.getbuffer().nbytes,
            filename=filename,
            headers=request.headers,
        )
    )


@router.get("/file/{uuid}/", response_model=UploadedFile)
@version(0)
@inject
async def get_file(
    uuid: UUID,
    repo: IRepo[File] = Depends(Provide[Container.file_repo]),
):
    file = await repo.get_by_id(uuid)
    return UploadedFile(
        uuid=file.uuid,
        path=file.path,
        size=file.size,
        format=file.format,
        name=file.name,
        ext=file.ext,
        created_at=file.created_at,
        updated_at=file.updated_at,
    )


@router.get(
    "/file/{uuid}/download/",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "headers": {
                "Content-Disposition": {
                    "description": "Content disposition header",
                    "type": "string",
                    "example": 'attachment; filename="image.png"',
                }
            },
        }
    },
)
@version(0)
@inject
async def download_file(
    uuid: UUID,
    repo: IRepo[File] = Depends(Provide[Container.file_repo]),
):
    file = await repo.get_by_id(uuid)
    return FileResponse(
        file.path,
        headers={"Content-Disposition": f'attachment; filename="{file.name}"'},
        media_type="application/octet-stream",
        filename=file.name,
    )


@router.get(
    "/file/{uuid}/stream/",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "headers": {
                "Content-Disposition": {
                    "description": "Content disposition header",
                    "type": "string",
                    "example": 'attachment; filename="image.png"',
                }
            },
        }
    },
)
@version(0)
@inject
async def stream_file(
    uuid: UUID,
    repo: IRepo[File] = Depends(Provide[Container.file_repo]),
):
    file = await repo.get_by_id(uuid)
    return StreamingResponse(
        chunk_file(file.path),
        headers={"Content-Disposition": f'attachment; filename="{file.name}"'},
        media_type="application/octet-stream",
    )
