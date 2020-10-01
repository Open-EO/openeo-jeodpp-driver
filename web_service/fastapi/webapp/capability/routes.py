import json
import logging


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi import Request


from . import service
from .. import models


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=models.BackEndCapabilities,
    summary="Returns general information about the back-end, including which version and endpoints of the openEO API are supported. May also include billing information.",
)
def view_service_capabilities(request: Request):
    capabilities_data = service.get_capabilities(request)
    return capabilities_data
