from enum import Enum
import logging
import datetime
from typing import List, Optional, Union


import sqlalchemy as sa

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import validator
from pydantic import Field
import shapely.wkt


from .base import Base
from .base import TimeStampMixin
from .base import PydanticBase
from .base import StacLinks


logger = logging.getLogger(__name__)


__all__ = [
    "Collection",
    "ViewCollectionAll",
    "CollectionBase",
    "CollectionViewJeodpp",
    "ViewCollectionAllOpeneo",
    "StacCollectionMetadata",
]


## Database model
class CollectionType(Base, TimeStampMixin):
    __tablename__ = "collection_type"
    oid = sa.Column(
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
    oid = sa.Column(sa.Integer, sa.Sequence("collection_oid_seq"), primary_key=True)
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
            "oid",
        ),
        sa.ForeignKeyConstraint(
            ["collection_type_ref"],
            ["collection_type.oid"],
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


class ProviderRole(str, Enum):
    producer = "producer"
    licensor = "licensor"
    processor = "processor"
    host = "host"


class DimenstionType(str, Enum):
    spatial = "spatial"
    temporal = "temporal"


class DimensionAxis(str, Enum):
    x = "x"
    y = "y"
    z = "z"


class StacProviders(PydanticBase):
    name: str
    description: Optional[str]
    roles: Optional[List[ProviderRole]]


class BoundingBox(PydanticBase):
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class CollectionTemporalExtent(PydanticBase):
    interval: List[List[Union[str, None]]]
    # One or more time intervals that describe the temporal extent of the dataset. The value null is supported and indicates an open time interval.


class CollectionSpatialExtent(PydanticBase):
    bbox: List[
        List[float]
    ]  # One or more bounding boxes that describe the spatial extent of the dataset. If multiple areas are provided, the union of the bounding boxes describes the spatial extent.


class CollectionExtent(PydanticBase):
    spatial: CollectionSpatialExtent
    temporal: CollectionTemporalExtent


class CubeSpatialDimension(PydanticBase):
    type: DimenstionType
    description: Optional[str] = Field(
        "string", description="Detailed description to explain the entity."
    )
    axis: Union[DimensionAxis]
    extent: Optional[List[int]]
    values: Optional[List[int]]
    step: Optional[int]
    reference_system: Union[str, int]


class CubeTemporalDimension(PydanticBase):
    type: str = "temporal"
    extent: List[Union[str, None]]


class CubeBands(PydanticBase):
    type: str = "bands"
    values: List[str]


class CollectionCubeDimension(PydanticBase):
    x: CubeSpatialDimension
    y: CubeSpatialDimension
    t: CubeTemporalDimension
    bands: CubeBands


class EOCloudCoverRange(PydanticBase):
    min: int = Field(0)
    max: int = Field(90)


class CollectionSummaries(PydanticBase):
    constellation: Optional[List[str]] = Field(["Sentinel2"])
    platform: Optional[List[str]] = Field(["Sentinel-2A", "Sentinel-2B"])
    instruments: Optional[List[str]] = Field(["MSI"])
    cloud_cover: Optional[EOCloudCoverRange] = Field(alias="eo:cloud_cover")


class StacCollectionMetadata(PydanticBase):
    stac_version: str
    stac_extensions: Optional[List[str]]
    id: str
    title: Optional[str]
    description: str
    keywords: Optional[List[str]]
    version: Optional[str]
    deprecated: Optional[bool] = False
    license: str
    providers: Optional[List[StacProviders]]
    extent: CollectionExtent
    links: List[StacLinks]
    cube_dimensions: CollectionCubeDimension = Field(
        description="Uniquely named dimensions of the data cube. The keys of the object are the dimension names. For interoperability, it is RECOMMENDED to use the following dimension names if there is only a single dimension with the specified criteria:",
        alias="cube:dimensions",
    )
    summaries: CollectionSummaries

    class Config:
        allow_population_by_alias = True


class CollectionBase(PydanticBase):
    collection_id: str
    collection_metadata: StacCollectionMetadata
    collection_footprint: str
    collection_jeolab: bool = False


class CollectionViewJeodpp(CollectionBase):
    # The footprint we retrieve from the database is a WKBElement instance
    # So we need to convert it to WKT
    @validator("collection_footprint", pre=True)
    def _footprint_to_wkt(cls, v):
        wkt = to_shape(v).wkt
        return wkt


class ViewCollectionAll(PydanticBase):
    collections: List[CollectionViewJeodpp]
    # links: List[StacLinks]


class ViewCollectionAllOpeneo(PydanticBase):
    collections: List[StacCollectionMetadata]
    links: List[StacLinks]
