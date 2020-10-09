import json
import logging
from typing import List


from sqlalchemy.orm import Session
from sqlalchemy.orm import Query


from ..models import Collection, CollectionBase

logger = logging.getLogger(__name__)


def get_query(
    *,
    db_session: Session,
    collection_id: str = None,
) -> Query:
    """ Return a Collection Query. """
    query = db_session.query(Collection)
    if collection_id:
        query = query.filter(Collection.collection_id == collection_id)
    return query


def get_query_openeo(
    *,
    db_session: Session,
    collection_id: str = None,
) -> Query:
    """ Return a Collection Query. """
    query = db_session.query(
        Collection.collection_metadata["id"].label("id"),
        Collection.collection_metadata["title"].label("title"),
        Collection.collection_metadata["version"].label("version"),
        Collection.collection_metadata["stac_version"].label("stac_version"),
        Collection.collection_metadata["stac_extensions"].label("stac_extensions"),
        Collection.collection_metadata["description"].label("description"),
        Collection.collection_metadata["links"].label("links"),
        Collection.collection_metadata["extent"].label("extent"),
        Collection.collection_metadata["license"].label("license"),
        Collection.collection_metadata["providers"].label("providers"),
        Collection.collection_metadata["keywords"].label("keywords"),
        Collection.collection_metadata["deprecated"].label("deprecated"),
        Collection.collection_metadata["cube:dimensions"].label("cube:dimensions"),       
    )
    if collection_id:
        query = query.filter(Collection.collection_metadata["id"].astext == collection_id)
    return query


def get_collection_all(*, db_session: Session) -> List[Collection]:
    query = get_query(db_session=db_session)
    collection_records = query.all()
    return collection_records


def get_collection_all_openeo(*, db_session: Session) -> List[Collection]:
    query = get_query_openeo(db_session=db_session)
    collection_records = query.all()
    return collection_records


def get_collection_by_id(*, db_session: Session, collection_id: str):
    query = get_query(db_session=db_session, collection_id=collection_id)
    collection_record = query.one_or_none()
    return collection_record


def get_collection_by_id_openeo(*, db_session: Session, collection_id: str):
    query = get_query_openeo(db_session=db_session, collection_id=collection_id)
    collection_record = query.one_or_none()
    return collection_record


def create(*, db_session: Session, collection_record_in: CollectionBase) -> Collection:
    """Create a new Collection. """
    collection_record = Collection(**collection_record_in.dict())
    db_session.add(collection_record)
    db_session.commit()
    return collection_record


def update(
    *, db_session: Session, collection_id: str, collection_record_update: CollectionBase
) -> Collection:
    """Update existing Collection. """
    db_session.query(Collection).filter(
        Collection.collection_id == collection_id
    ).update(collection_record_update.dict())
    db_session.commit()
    query = get_query(db_session=db_session, collection_id=collection_id)
    updated_collection_record = query.one_or_none()
    return updated_collection_record


def delete(*, db_session: Session, collection_id: str) -> str:
    deleted_collection_id = (
        db_session.query(Collection)
        .filter(Collection.collection_id == collection_id)
        .delete()
    )
    return deleted_collection_id
