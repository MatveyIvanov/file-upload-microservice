import io
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import BackgroundTasks, Depends, Header, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi_versioning import version

from config.di import Container
from models.file import File
from schemas.files import UploadedFile
from services.interfaces import ICreateFile, ISaveFileToExternalStorage
from utils.http import safe_filename
from utils.exceptions import Custom400Exception
from utils.file import chunk_file
from utils.repo import IRepo
from utils.routing import APIRouter

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/file/", response_model=UploadedFile)
@version(0)
@inject
async def upload_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    create_file: ICreateFile = Depends(Provide[Container.create_file]),
    save_to_s3: ISaveFileToExternalStorage = Depends(
        Provide[Container.save_file_to_s3]
    ),
) -> UploadedFile:
    instance = await create_file(file)
    background_tasks.add_task(save_to_s3, instance.uuid)
    return instance


@router.post("/file/stream/", response_model=UploadedFile)
@version(0)
@inject
async def stream_upload_file(
    request: Request,
    filename: Annotated[str, Header()],
    content_type: Annotated[str, Header(regex=r"application/octet-stream")],
    background_tasks: BackgroundTasks,
    create_file: ICreateFile = Depends(Provide[Container.create_file]),
    save_to_s3: ISaveFileToExternalStorage = Depends(
        Provide[Container.save_file_to_s3]
    ),
) -> UploadedFile:
    buffer = io.BytesIO()
    async for chunk in request.stream():
        buffer.write(chunk)

    buffer.seek(0)
    instance = await create_file(
        file=UploadFile(
            file=buffer,
            size=buffer.getbuffer().nbytes,
            filename=filename,
            headers=request.headers,
        )
    )
    background_tasks.add_task(save_to_s3, instance.uuid)
    return instance


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
        available_for_download=file.is_removed_from_disk is False,
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
    if file.is_removed_from_disk:
        # S3 could be integrated in that case.
        raise Custom400Exception("File is not available for download.")
    return FileResponse(
        file.path,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename(file.name)}"'
        },
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
    if file.is_removed_from_disk:
        # S3 could be integrated in that case.
        raise Custom400Exception("File is not available for download.")
    return StreamingResponse(
        chunk_file(file.path),
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename(file.name)}"'
        },
        media_type="application/octet-stream",
    )
