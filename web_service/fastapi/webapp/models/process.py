from typing import Any

from .base import PydanticBase

__all__ = ["ProcessGraph"]


class ProcessGraph(PydanticBase):
    process_id: str
    process_description: str
    property: str
