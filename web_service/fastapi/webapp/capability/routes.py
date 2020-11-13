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


@router.get(
    "/file_formats",
    response_model=models.IOFileFormats,
    summary="The request will ask the back-end for supported input and output file formats. Input file formats specify which file a back-end can read from. Output file formats specify which file a back-end can write to.",
)
def view_file_formats(request: Request):
    file_formats_data = service.get_file_formats(request)
    return file_formats_data


@router.get(
    "/udf_runtimes",
    response_model=models.SupportedRuntimes,
    response_model_exclude_none=True,
    summary="Returns the supported runtimes for user-defined functions (UDFs), which includes either the programming languages including version numbers and available libraries including version numbers or docker containers.",
)
def view_udf_runtimes(request: Request):
    udf_runtimes_data = service.get_udf_runtimes(request)
    return udf_runtimes_data


@router.get(
    "/service_types",
    response_model=models.SupportedWebService,
    response_model_exclude_none=True,
    summary="The request will ask the back-end for supported secondary web service protocols such as OGC WMS, OGC WCS, OGC API - Features or XYZ tiles. The response is an object of all available secondary web service protocols with their supported configuration settings and expected process parameters.",
)
def view_ogc_services(request: Request):
    ogc_services_data = service.get_ogc_services(request)
    return ogc_services_data
