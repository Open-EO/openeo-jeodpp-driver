import functools
import logging
import os

from typing import Any
from typing import Iterator

import sqlalchemy

from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from .settings import get_settings


project_name = os.environ.get("PROJECT_NAME")

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = sqlalchemy.MetaData(naming_convention=NAMING_CONVENTION, schema=project_name)
Base = declarative_base(metadata=metadata)


@functools.lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    """ This function could be replaced with a global variable if preferred """
    settings = get_settings()
    return FastAPISessionMaker(settings.db_uri)


def get_db() -> Iterator[Session]:
    """ FastAPI dependency that provides a sqlalchemy session """
    yield from _get_fastapi_sessionmaker().get_db()


def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""
    mapped_name = resolve_table_name(table_fullname)
    for c in Base._decl_class_registry.values():
        if hasattr(c, "__table__") and c.__table__.fullname == mapped_name:
            return c
    raise Exception(
        f"Incorrect tablename '{mapped_name}'. Check the name of your model."
    )
