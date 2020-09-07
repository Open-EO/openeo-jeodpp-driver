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
    "/",
    summary="The request asks the back-end for available processes and returns detailed process descriptions, including parameters and return values. Processes are described using the Functio specification for language-agnostic process descriptions",
)
def view_process_all():
    processes = service.get_process_all()
    if not processes:
        raise HTTPException(status_code=404, detail=f"No processes have been created")
    return processes


@router.get(
    "/{process_name}",
    summary="The request will ask the back-end for further details about a process specified by the identifier process_name",
)
def view_process_detail(process_name: str):
    process = service.get_process_by_id(process_name)
    if not process:
        raise HTTPException(
            status_code=404,
            detail=f"No process with id {process_name} have been created",
        )
    return process
