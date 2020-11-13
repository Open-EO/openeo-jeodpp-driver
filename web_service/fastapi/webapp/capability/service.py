import json
import logging
from typing import List


from ..models import BackEndCapabilities, OpeneoAPIVersions, IOFileFormats

logger = logging.getLogger(__name__)


def get_available_openapi_endpoints():
    return [
        {"path": "/", "methods": ["GET"]},
        {"path": "/file_formats", "methods": ["GET"]},
        {"path": "/udf_runtimes", "methods": ["GET"]},
        {"path": "/collections", "methods": ["GET"]},
        {"path": "/collections/{collection_id}", "methods": ["GET"]},
        {"path": "/processes", "methods": ["GET"]},
        {"path": "/processes/{process_name}", "methods": ["GET"]},
        {"path": "/jobs", "methods": ["GET"]},
        {"path": "/jobs", "methods": ["POST"]},
        {"path": "/jobs/{job_id}", "methods": ["GET"]},
        {"path": "/jobs/{job_id}", "methods": ["PATCH"]},
        {"path": "/jobs/{job_id}", "methods": ["DELETE"]},
        # {"path": "/jobs/{job_id}/results", "methods": ["POST"]},
    ]


def get_available_links(request):
    request_url = str(request.url)

    return [
        {
            "rel": "service-desc",
            "href": f"{request_url}/openeo/openapi.json",
            "title": "OpenAPI json",
            "type": "application/json",
        },
        # {
        #   "rel": "service-doc",
        #  "href": f"{request_url}docs",
        # "title": "Swagger UI",
        # "type": "text/html",
        # },
    ]


def get_billing_information():
    return {
        "currency": None,
        "default_plan": "Free to all EC staff",
    }


def get_capabilities(request) -> BackEndCapabilities:
    capabilities = {
        "api_version": "1.0.0",
        "backend_version": "0.0.1",
        "stac_version": "0.9.0",
        "id": "https://jeodpp.jrc.ec.europa.eu/services/openeo/",
        "title": "JEODPP OpenEO Application Programming Interface (API)",
        "description": "Testing instance of the JEODPP OpenEO API provides programming interface to collect information about available collections, processes and allows to submit a job.",
        "production": False,
        "endpoints": get_available_openapi_endpoints(),
        "billing": get_billing_information(),
        "links": get_available_links(request),
    }
    return capabilities


def get_service_versions(request) -> OpeneoAPIVersions:
    request_url = str(request.url)
    base_url = "https://jeodpp.jrc.ec.europa.eu/openeo/"
    versions_response = {
        "versions": [{"url": base_url, "production": False, "api_version": "1.0.0"}]
    }
    return versions_response


def get_file_formats(request) -> IOFileFormats:
    formats_response = {
        "input": {
            "GTiff": {
                "title": "GeoTiff",
                "description": "GeoTIFF is format extension for storing georeference and geocoding information in a TIFF 6.0 compliant raster file by tying a raster image to a known model space or map projection.",
                "gis_data_types": ["raster"],
                "parameters": {},
            }
        },
        "output": {
            "GTiff": {
                "title": "GeoTiff",
                "description": "GeoTIFF is format extension for storing georeference and geocoding information in a TIFF 6.0 compliant raster file by tying a raster image to a known model space or map projection.",
                "gis_data_types": ["raster"],
                "parameters": {},
            }
        },
    }
    return formats_response
