import json
import logging
from typing import List


from sqlalchemy.orm import Session
from sqlalchemy.orm import Query


from ..models import Process

logger = logging.getLogger(__name__)


def get_query(
    *,
    db_session: Session,
    id: str = None,
) -> Query:
    """ Return a Process Query. """
    query = db_session.query(Process)
    if id:
        query = query.filter(Process.id == id)
    return query


def get_process_all(*, db_session: Session) -> List[Process]:
    query = get_query(db_session=db_session)
    process_records = query.all()
    return process_records
