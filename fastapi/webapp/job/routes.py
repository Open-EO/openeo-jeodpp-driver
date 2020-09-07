import json
import logging


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status


from . import service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/output_formats",
    summary="The request will ask the back-end for supported output formats, e.g. PNG, GTiff and JSON, and its default output format. The response is an object of the default and all available output formats and their options. This does not include the supported secondary web services",
)
def view_output_formats_all():
    output_formats = service.get_output_formats_all()
    if not output_formats:
        raise HTTPException(status_code=404, detail=f"No output_formats have been created")
    return output_formats


@router.get(
    "/",
    summary="Requests to this endpoint will list all batch jobs submitted by a user with given id",
)
def view_jobs_all():
    jobs = service.get_jobs_all()
    if not jobs:
        raise HTTPException(
            status_code=404,
            detail=f"No jobs have been created",
        )
    return jobs


@router.get(
    "/{job_id}",
    summary="Returns detailed information about a submitted batch job",
)
def view_job_by_id(job_id):
    job = service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"No job with id {job_id} have been created"
        )
    return job
