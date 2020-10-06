import json
import logging
from typing import List


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


@router.get(
    "/.well-known/openeo",
    response_model=models.OpeneoAPIVersions,
    summary="Well-Known URI (see RFC 5785) for openEO, listing all implemented openEO versions supported by the service provider.",
)
def get_service_versions(request: Request):
    versions_data = service.get_service_versions(request)
    return versions_data
