from enum import Enum
import logging
import datetime


import sqlalchemy as sa

from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB


from .base import Base
from .base import TimeStampMixin
from .base import PydanticBase


logger = logging.getLogger(__name__)


__all__ = ["Collection"]


## Database model
class CollectionType(Base, TimeStampMixin):
    __tablename__ = "collection_type"
    collection_type_oid = sa.Column(
        sa.Integer, sa.Sequence("collection_type_oid_seq"), primary_key=True
    )
    collection_type_name = sa.Column(sa.String, nullable=False, unique=True)
    collection_type_metadata = sa.Column(JSONB, nullable=False)

    __table_args = (
        sa.PrimaryKeyConstraint("oid"),
        sa.Index(
            "idx_collection_type_name", "collection_type_name", postgresql_using="btree"
        ),
        sa.Index(
            "idx_collection_type_metadata",
            "collection_type_metadata",
            postgresql_using="gin",
        ),
    )


class Collection(Base, TimeStampMixin):
    __tablename__ = "collection"
    collection_oid = sa.Column(
        sa.Integer, sa.Sequence("collection_oid_seq"), primary_key=True
    )
    collection_id = sa.Column(sa.String, nullable=False, unique=True)
    collection_footprint = sa.Column(
        Geometry("MULTIPOLYGON", srid=4326, spatial_index=False), nullable=False
    )  # server_default=sa.func.ST_GeomFromText(FOOTPRINT_DEFAULT, 4326))
    collection_metadata = sa.Column(JSONB, nullable=False)
    collection_history = sa.Column(JSONB, nullable=True)
    collection_jeolab = sa.Column(sa.Boolean, nullable=False)
    collection_type_ref = sa.Column(sa.Integer, unique=True, nullable=True)

    __table_args__ = (
        sa.PrimaryKeyConstraint(
            "collection_oid",
        ),
        sa.ForeignKeyConstraint(
            ["collection_type_ref"],
            ["collection_type.collection_type_oid"],
        ),
        sa.Index(
            "idx_collection_identifier", "collection_id", postgresql_using="btree"
        ),
        sa.Index(
            "idx_collection_footprint", "collection_footprint", postgresql_using="gist"
        ),
        sa.Index(
            "idx_collection_metadata", "collection_metadata", postgresql_using="gin"
        ),
        sa.Index(
            "idx_collection_history", "collection_history", postgresql_using="gin"
        ),
    )
