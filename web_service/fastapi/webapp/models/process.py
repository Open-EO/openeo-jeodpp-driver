from typing import Any, Optional, List


import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


from .base import PydanticBase
from .base import Base
from .base import TimeStampMixin
from .base import StacLinks

__all__ = ["ProcessGraph", "Process","ViewProcessAll"]


#SQLAlchemy models
class Process(Base, TimeStampMixin):
    __tablename__ = "process"
    id = sa.Column(sa.String, nullable=False, unique=True, primary_key=True)
    summary = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=False)
    categories = sa.Column(JSONB, nullable=True)
    parameters = sa.Column(JSONB, nullable=False)
    returns = sa.Column(JSONB, nullable=False)
    deprecated = sa.Column(sa.Boolean, default=False)
    experimental = sa.Column(sa.Boolean, default=False)
    exceptions = sa.Column(JSONB, nullable=True)
    examples = sa.Column(JSONB, nullable=True)
    links = sa.Column(JSONB, nullable=True)
    process_graph = sa.Column(JSONB, nullable=True)
    

    __table_args__ = (
        sa.PrimaryKeyConstraint(
            "id",
        ),
        sa.Index(
            "idx_process_identifier", "id", postgresql_using="btree"
        ),
        sa.Index(
            "idx_process_description", "description", postgresql_using="btree"
        ),
        sa.Index(
            "idx_process_parameters", "parameters", postgresql_using="gin"
        ),
        sa.Index(
            "idx_process_categories", "categories", postgresql_using="gin"
        ),
        sa.Index(
            "idx_process_returns", "returns", postgresql_using="gin"
        ),
    )



#Pydantic models
class ProcessGraph(PydanticBase):
    process_id: str
    process_description: str
    property: str


class ProcessMetadata(PydanticBase):
    id: str
    summary: Optional[str]
    description: str
    categories: Optional[List[str]]
    parameters: List[dict]
    returns: dict
    deprecated: Optional[bool]
    experimental: Optional[bool]
    exception: Optional[dict]
    examples: Optional[List[dict]]
    links: Optional[List[dict]]
    process_graph: Optional[dict]


class ViewProcessAll(PydanticBase):
    processes: List[ProcessMetadata]
    links: List[StacLinks]
