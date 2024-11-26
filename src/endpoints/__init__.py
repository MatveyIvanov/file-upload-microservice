from typing import Tuple

from endpoints.upload import router as upload_router
from utils.routing import APIRouter


def get_routers() -> Tuple[APIRouter, ...]:
    return (upload_router,)
