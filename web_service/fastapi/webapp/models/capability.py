from enum import Enum
import logging
import datetime
from typing import List, Optional


from pydantic import Field
from pydantic import HttpUrl


from .base import Base
from .base import TimeStampMixin
from .base import PydanticBase
from .base import StacLinks


logger = logging.getLogger(__name__)


__all__ = [
    "BackEndCapabilities",
    "OpeneoAPIVersions",
    "IOFileFormats",
    "SupportedRuntimes",
    "SupportedWebService",
]


## Pydantic models


class GisDataTypes(str, Enum):
    raster = "raster"
    vector = "vector"
    table = "table"
    other = "other"


class UDFruntimeType(str, Enum):
    language = "language"
    docker = "docker"


class Endpoint(PydanticBase):
    path: str
    methods: List[str]


class Plan(PydanticBase):
    name: str = Field(
        description="Name of the plan. Is allowed to be case insensitive throughout the API."
    )
    description: str = Field(
        description="A description that gives a rough overview over the plan."
    )
    paid: bool = Field(
        False,
        decription="Indicates whether the plan is a paid plan (true) or a free plan (false).",
    )
    url: Optional[str] = Field(
        description="URL to a web page with more details about the plan."
    )


class Billing(PydanticBase):
    currency: str = Field(
        None,
        description="The currency the back-end is billing in. The currency MUST be either a valid currency code as defined in ISO-4217 or a proprietary currency, e.g. tiles or back-end specific credits. If set to the default value null, budget and costs are not supported by the back-end and users can't be charged.",
    )
    default_plan: Optional[str] = Field(
        "Free to all EC staff",
        description="Name of the default plan to use when the user doesn't specify a plan. Is allowed to be case insensitive throughout the API.",
    )
    plan: Optional[List[Plan]]


class BackEndCapabilities(PydanticBase):
    api_version: str = Field(
        "1.0.0",
        description="Version number of the openEO specification this back-end implements.",
    )
    backend_version: str
    stac_version: str
    id: str
    title: str
    description: str
    production: bool = False
    endpoints: List[Endpoint]
    billing: Billing
    links: List[StacLinks]


class OpenEOVersion(PydanticBase):
    url: HttpUrl = Field(description="Absolute URL to the service.")
    production: Optional[bool] = Field(
        False,
        description="Specifies whether the implementation is ready to be used in production use (true) or not (false). Clients SHOULD only connect to non-production implementations if the user explicitly confirmed to use a non-production implementation. This flag is part of GET /.well-known/openeo and GET /. It MUST be used consistently in both endpoints",
    )
    api_version: str = Field(
        "1.0.0",
        description="Version number of the openEO specification this back-end implements",
    )


class OpeneoAPIVersions(PydanticBase):
    versions: List[OpenEOVersion]


class FileFormat(PydanticBase):
    title: Optional[str]
    description: Optional[str]
    gis_data_types: List[GisDataTypes]
    parameters: dict = {}


class FileFormats(PydanticBase):
    GTiff: FileFormat


class IOFileFormats(PydanticBase):
    input: FileFormats
    output: FileFormats


class UDFRuntime(PydanticBase):
    title: Optional[str]
    description: Optional[str]
    type: UDFruntimeType
    default: str
    links: Optional[List[StacLinks]]
    versions: dict


class SupportedRuntimes(PydanticBase):
    python: UDFRuntime


class OGCWebService(PydanticBase):
    title: Optional[str]
    description: Optional[str]
    configuration: dict
    process_parameters: List[dict]
    links: Optional[List[StacLinks]]


class SupportedWebService(PydanticBase):
    wms: OGCWebService
