from dependency_injector.wiring import Provide, inject
from fastapi import Depends, UploadFile
from fastapi_versioning import version

from config.di import Container
from schemas.files import UploadedFile
from services.interfaces import ICreateFile
from utils.routing import APIRouter


router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/file/", response_model=UploadedFile)
@version(0)
@inject
async def file(
    file: UploadFile,
    create_file: ICreateFile = Depends(Provide[Container.create_file]),
):
    print(file.__dict__)
    print(type(create_file))
    return await create_file(file)
