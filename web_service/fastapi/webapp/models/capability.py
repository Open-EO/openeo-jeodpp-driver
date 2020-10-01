from enum import Enum
import logging
import datetime
from typing import List, Optional


from pydantic import Field


from .base import Base
from .base import TimeStampMixin
from .base import PydanticBase
from .base import StacLinks


logger = logging.getLogger(__name__)


__all__ = ["BackEndCapabilities"]


## Pydantic models
class Endpoint(PydanticBase):
    path: str
    methods: List[str]


class Plan(PydanticBase):
    name: str = Field(description="Name of the plan. Is allowed to be case insensitive throughout the API.")
    description: str = Field(description="A description that gives a rough overview over the plan.")
    paid: bool = Field(False, decription="Indicates whether the plan is a paid plan (true) or a free plan (false).")
    url: Optional[str] = Field(description="URL to a web page with more details about the plan.")


class Billing(PydanticBase):
    currency: str = Field(None, description="The currency the back-end is billing in. The currency MUST be either a valid currency code as defined in ISO-4217 or a proprietary currency, e.g. tiles or back-end specific credits. If set to the default value null, budget and costs are not supported by the back-end and users can't be charged.")
    default_plan: str = Field("Free to all EC staff", description="Name of the default plan to use when the user doesn't specify a plan. Is allowed to be case insensitive throughout the API." )
    plan: List[Plan]

class BackEndCapabilities(PydanticBase):
    api_version: str = Field("1.0.0", description="Version number of the openEO specification this back-end implements.")
    backend_version: str
    stac_version: str
    id: str
    title: str
    description: str
    production: bool = False
    endpoints: List[Endpoint]
    billing: Optional[Billing]
    links: List[StacLinks]
