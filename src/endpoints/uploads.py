from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, UploadFile
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


@router.get("/file/{uuid}/download/", response_class=FileResponse)
@version(0)
@inject
async def download_file(
    uuid: UUID,
    repo: IRepo[File] = Depends(Provide[Container.file_repo]),
):
    file = await repo.get_by_id(uuid)
    print(file.path, file.name, file.format)
    return FileResponse(
        file.path,
        media_type="application/octet-stream",
        filename=file.name,
    )


@router.get("/file/{uuid}/stream/", response_class=StreamingResponse)
@version(0)
@inject
async def stream_download_file(
    uuid: UUID,
    repo: IRepo[File] = Depends(Provide[Container.file_repo]),
):
    file = await repo.get_by_id(uuid)
    print(file.path, file.name, file.format)

    headers = {"Content-Disposition": f'attachment; filename="{file.name}"'}
    return StreamingResponse(
        chunk_file(file.path),
        headers=headers,
        media_type="application/octet-stream",
    )
