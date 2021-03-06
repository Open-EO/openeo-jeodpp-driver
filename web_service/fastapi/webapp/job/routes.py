import json
import logging
from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi import Response
from fastapi import Request
from sqlalchemy.orm import Session
import sqlalchemy.exc
import psycopg2.errors


from . import service
from .. import models
from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Requests to this endpoint will list all batch jobs submitted by a user with given id",
    response_model=models.ViewJobAll,
    response_model_exclude_none=True,
)
def view_job_all(db_session: Session = Depends(get_db)):
    jobs_records = service.get_job_all(db_session=db_session)
    if not jobs_records:
        raise HTTPException(
            status_code=404,
            detail=f"No jobs have been created",
        )
    response_data = {
        "jobs": jobs_records,
        "links": [
            {
                "rel": "self",
                "href": "https://jeodpp.jrc.ec.europa.eu/openeo/jobs",
                "title": "List of Jobs",
            },
        ],
    }
    return response_data


@router.post(
    "",
    response_model=models.JobMetadata,
    summary="Create a new job record",
    status_code=status.HTTP_201_CREATED,
)
def create_job_record(
    request: Request,
    response: Response,
    job_record_in: models.CreateJobMetadata,
    db_session: Session = Depends(get_db),
):
    try:
        job_record = service.create_job(
            db_session=db_session, job_record_in=job_record_in
        )
    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InternalError) as exc:
        if isinstance(exc.orig, psycopg2.errors.UniqueViolation):
            msg = f"A job record with the id {job_record_in.id} already exists"
        else:
            msg = "Creation of Job failed. Please check the logs."
        raise HTTPException(status_code=422, detail=msg)
    print(job_record)
    response.headers["OpenEO-Identifier"] = job_record.id
    response.headers["Location"] = f"{request.url}/{job_record.id}"
    return job_record


@router.patch(
    "/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Update job metadata"
)
def update_job_metadata(
    job_id: UUID,
    job_record_in: models.CreateJobMetadata,
    db_session: Session = Depends(get_db),
) -> None:
    try:
        service.update_job(
            db_session=db_session, job_id=str(job_id), job_record_in=job_record_in
        )
    except sqlalchemy.exc.IntegrityError as exc:
        raise HTTPException(status_code=422, detail=exc)


@router.get(
    "/{job_id}",
    response_model=models.JobMetadata,
    response_model_exclude_none=True,
    summary="The request will ask the back-end for further details about a job specified by the identifier collection_name",
)
def view_job_detail(job_id: UUID, db_session: Session = Depends(get_db)):
    job = service.get_job_by_id(job_id=str(job_id), db_session=db_session)
    raise HTTPException(
        status_code=404,
        detail=f"No job with id {job_id} have been created",
    )
    return job


@router.delete(
    "/{job_id}", summary="Remove job by its id", status_code=status.HTTP_204_NO_CONTENT
)
def remove_collection_record(job_id: UUID, db_session: Session = Depends(get_db)):
    try:
        deleted_job_id = service.delete_job_by_id(
            db_session=db_session, job_id=str(job_id)
        )
    except sqlalchemy.exc.IntegrityError as exc:
        raise HTTPException(status_code=422, detail=exc)


@router.get(
    "/{job_id}/estimate",
    response_model=models.JobEstimate,
    response_model_exclude_none=True,
    summary="Clients can ask for an estimate for a batch job. Back-ends can decide to either calculate the duration, the costs, the size or a combination of them. This MUST be the upper limit of the incurring costs. Clients can be charged less than specified, but never more. Back-end providers MAY specify an expiry time for the estimate. Starting to process data afterwards MAY be charged at a higher cost. Costs MAY NOT include downloading costs. This can be indicated with the downloads_included flag",
)
def view_job_estimate(job_id: UUID):
    job_estimate_data = service.get_job_estimate(str(job_id))
    return job_estimate_data


@router.post(
    "/{job_id}/resuls",
    summary="Adds a batch job to the processing queue to compute the results.",
    status_code=status.HTTP_202_ACCEPTED,
)
def start_batch_job(job_id: UUID, db_session: Session = Depends(get_db)):
    job_status = service.start_batch_job(db_session=db_session, job_id=str(job_id))
    if job_status in ["queued", "running"]:
        raise HTTPException(
            status_code=409,
            detail=f"Job with id {job_id} is {job_status}",
        )


@router.delete(
    "/{job_id}/results",
    summary="Cancels all related computations for this job at the back-end. It will stop generating additional costs for processing.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_batch_job(job_id: UUID, db_session: Session = Depends(get_db)):
    job_status = service.cancel_batch_job(db_session=db_session, job_id=job_id)
    if job_status not in ["created", "canceled"]:
        raise HTTPException(
            status_code=500, detail=f"Job with id {job_id} has not been canceled {job_status}"
        )