import json
import logging
from typing import List


from sqlalchemy.orm import Session
from sqlalchemy.orm import Query


from ..models import Collection

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


def get_collection_all(*, db_session: Session) -> List[Collection]:
    query = get_query(db_session=db_session)
    collection_records = query.all()
    return collection_records


def get_collection_by_id(*, db_session: Session, collection_id: str):
    query = get_query(db_session=db_session, collection_id=collection_id)
    collection_record = query.one_or_none()
    return collection_record
