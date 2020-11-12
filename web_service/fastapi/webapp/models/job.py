import datetime
from enum import Enum
from typing import Any, Optional, List

import pydantic
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func


from .base import PydanticBase
from .base import Base
from .base import TimeStampMixin
from .base import StacLinks
from .process import ProcessMetadata

__all__ = ["Job", "ViewJobAll", "CreateJobMetadata", "JobMetadata"]


# SQLAlchemy models


class ProcessStatus(str, Enum):
    created = "created"
    queued = "queued"
    running = "running"
    canceled = "canceled"
    finished = "finished"
    error = "error"


class Job(Base, TimeStampMixin):
    __tablename__ = "job"
    id = sa.Column(UUID, primary_key=True, server_default=sa.text("uuid_generate_v4()"))
    title = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=True)
    process = sa.Column(JSONB, nullable=False)
    status = sa.Column(sa.String, nullable=False, server_default=str("created"))
    progress = sa.Column(sa.Integer, nullable=True)
    plan = sa.Column(sa.String, nullable=True)
    costs = sa.Column(sa.Float, nullable=True)
    budget = sa.Column(sa.Integer, nullable=True)

    __table_args__ = (
        sa.PrimaryKeyConstraint(
            "id",
        ),
        sa.Index("idx_job_title", "title", postgresql_using="btree"),
        sa.Index("idx_job_description", "description", postgresql_using="btree"),
        sa.Index("idx_job_process", "process", postgresql_using="gin"),
        sa.Index("idx_job_status", "status", postgresql_using="btree"),
    )


# Pydantic models
class JobProcessMetadata(PydanticBase):
    id: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    parameters: Optional[dict]
    returns: Optional[dict]
    categories: Optional[List[str]]
    deprecated: Optional[bool] = pydantic.Field(False)
    experimental: Optional[bool] = pydantic.Field(False)
    exceptions: Optional[dict]
    examples: Optional[List[dict]]
    links: Optional[List[dict]]
    process_graph: dict


class ViewJobMetadata(PydanticBase):
    title: Optional[str] = pydantic.Field(None)
    description: Optional[str] = pydantic.Field(None)
    process: Optional[JobProcessMetadata]
    status: ProcessStatus = pydantic.Field(ProcessStatus.created)
    progress: Optional[int] = pydantic.Field(0, ge=0, le=100)
    plan: Optional[str] = pydantic.Field(None)
    costs: Optional[float]
    budget: Optional[int]


class CreateJobMetadata(PydanticBase):
    title: Optional[str] = pydantic.Field(None)
    description: Optional[str] = pydantic.Field(None)
    process: JobProcessMetadata
    plan: Optional[str] = pydantic.Field(None)
    budget: Optional[int]


class JobMetadata(ViewJobMetadata):
    id: str
    created: datetime.datetime
    updated: Optional[datetime.datetime]


class ViewJobAll(PydanticBase):
    jobs: List[JobMetadata]
    links: List[StacLinks]


"""
class OutputFormatParameters(PydanticBase):
    tiles: bool = True
    compress: str = "jpeg"
    photometric: str = "YCBCR"
    jpeg_quality: int = 80


class OutputFormat(PydanticBase):
    format: str = "GTiff"
    parameters: OutputFormatParameters


class JobTaskCreate(PydanticBase):
    title: str = "NDVI based on Sentinel 2"
    description: str
    process_graph: ProcessGraph
    output: OutputFormat
    plan: str = "free"
    budget: int = 100
"""
