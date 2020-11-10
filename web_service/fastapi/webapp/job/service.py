import json
import logging
from typing import List


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
        query = query.filter(Job.id == job_id)
    return query


def get_job_all(*, db_session: Session) -> List[models.Job]:
    query = get_query(db_session=db_session)
    job_records = query.all()
    return job_records

'''
def get_job_by_id(job_id):
    matching_job = None
    for job in _JOBS_DATA.get("jobs"):
        for k, v in job.items():
            if k == "job_id" and v == str(job_id):
                matching_job = job
            else:
                continue
    return matching_job


def create_job(job_payload_data):
    insert_job_record = job_payload_data.dict()
    insert_job_record["job_id"] = str(uuid.uuid4())
    _JOBS_DATA.get("jobs").append(insert_job_record)
    return _JOBS_DATA


def update_job(job_id, job_payload_data):
    for job in _JOBS_DATA.get("jobs"):
        for k, v in job.items():
            if k == "job_id" and v == str(job_id):
                updated_job_record = job_payload_data.dict()
                updated_job_record["job_id"] = str(job_id)
                job.update(updated_job_record)
            else:
                continue
    return job_id


def delete_job(job_id):
    for job in _JOBS_DATA.get("jobs"):
        for k, v in job.items():
            if k == "job_id" and v == str(job_id):
                _JOBS_DATA.get("jobs").remove(job)
            else:
                continue
    return job_id
'''