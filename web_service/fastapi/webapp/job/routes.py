import json
import logging
from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session


from . import service
from .. import models
from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/output_formats",
    summary="The request will ask the back-end for supported output formats, e.g. PNG, GTiff and JSON, and its default output format. The response is an object of the default and all available output formats and their options. This does not include the supported secondary web services",
)
def view_output_formats_all():
    output_formats = service.get_output_formats_all()
    if not output_formats:
        raise HTTPException(
            status_code=404, detail=f"No output_formats have been created"
        )
    return output_formats


@router.get(
    "",
    summary="Requests to this endpoint will list all batch jobs submitted by a user with given id",
    response_model=models.ViewJobAll
)
def view_job_all(db_session: Session = Depends(get_db)):
    jobs = service.get_job_all(db_session=db_session)
    if not jobs:
        raise HTTPException(
            status_code=404,
            detail=f"No jobs have been created",
        )
    return jobs

'''
@router.post(
    "/",
    summary="Creates a new batch processing task (job) from one or more (chained) processes at the back-end.",
    status_code=status.HTTP_201_CREATED,
)
def create_new_batch_processing_job(job_payload_data: models.JobTaskCreate):
    batch_job = service.create_job(job_payload_data)
    return batch_job


@router.get(
    "/{job_id}",
    summary="Returns detailed information about a submitted batch job",
)
def view_job_by_id(job_id: UUID):
    job = service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=404, detail=f"No job with id {job_id} have been created"
        )
    return job


@router.patch(
    "/{job_id}",
    summary="Modifies an existing job at the back-end but maintains the identifier. Changes can be grouped in a single request. Jobs can only be modified when the job is not queued or running.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def patch_processing_job(job_id: UUID, job_payload_data: models.JobTaskCreate):
    updated_job = service.update_job(job_id, job_payload_data)
    return updated_job


@router.delete(
    "/{job_id}",
    summary="Deletes all data related to this job. Computations are stopped and computed results are deleted. This job won't generate additional costs for processing.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_processing_job(job_id: UUID):
    deleted_job = service.delete_job(job_id)
    return deleted_job


@router.post(
    "/{job_id}/results",
    summary="Adds a batch job to the processing queue to compute the results.",
    status_code=status.HTTP_202_ACCEPTED,
)
def start_job_by_id(job_id: UUID):
    job = service.start_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404, detail=f"job with id {job_id} have not been started"
        )
    return job
'''