import datetime
from typing import Optional

import sqlalchemy as sa


from pydantic import BaseModel
from pydantic import HttpUrl

from sqlalchemy.sql import func
from sqlalchemy_mixins import ReprMixin
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime


from ..database import Base
from ..database import metadata


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc, CURRENT_TIMESTAMP')"


# SQLAlchemy models
class TimeStampMixin(object):
    """ Timestamping mixin"""

    created = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated = sa.Column(sa.DateTime(timezone=True), onupdate=func.now())

    created._creation_order = 9998
    updated._creation_order = 9998

    @staticmethod
    def _updated(mapper, connection, target):
        target.updated = datetime.datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        sa.event.listen(cls, "before_update", cls._updated)


# Pydantic models
class PydanticBase(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True


class StacLinks(BaseModel):
    rel: str
    href: HttpUrl
    #type: Optional[str]
    title: Optional[str]
