import datetime

from .base import PydanticBase
from .process import ProcessGraph


__all__ = ["JobTaskCreate", "OutputFormat"]


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
