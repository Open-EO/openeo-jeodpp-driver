import json
import logging
from typing import List
from uuid import UUID


from sqlalchemy.orm import Session
from sqlalchemy.orm import Query


from . import service
from .. import models
from ..database import get_db

logger = logging.getLogger(__name__)


def get_query(
    *,
    db_session: Session,
    job_id: str = None,
) -> Query:
    """ Return a Job Query. """
    query = db_session.query(models.Job)
    if job_id:
        query = query.filter(models.Job.id == job_id)
    return query


def get_job_all(*, db_session: Session) -> List[models.Job]:
    query = get_query(db_session=db_session)
    job_records = query.all()
    return job_records


def create_job(
    *, db_session: Session, job_record_in: models.CreateJobMetadata
) -> models.Job:
    """Create a new Job. """
    job_record = models.Job(**job_record_in.dict())
    db_session.add(job_record)
    db_session.commit()
    return job_record


def update_job(
    *, db_session: Session, job_id: UUID, job_record_in: models.CreateJobMetadata
) -> None:
    """Update existing Job. """
    db_session.query(models.Job).filter(models.Job.id == job_id).update(
        job_record_in.dict()
    )
    db_session.commit()
    # query = get_query(db_session=db_session, job_id=job_id)
    # updated_job_record = query.one_or_none()
    # return updated_job_record


def get_job_by_id(*, db_session: Session, job_id: UUID) -> models.Job:
    query = get_query(db_session=db_session, job_id=job_id)
    job_record = query.one_or_none()
    return job_record


def delete_job_by_id(*, db_session: Session, job_id: UUID) -> UUID:
    deleted_job_id = (
        db_session.query(models.Job).filter(models.Job.id == job_id).delete()
    )
    return deleted_job_id
