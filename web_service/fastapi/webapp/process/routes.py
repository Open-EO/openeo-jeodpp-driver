import json
import logging


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
    "",
    response_model = models.ViewProcessAll,
    summary="The request asks the back-end for available processes and returns detailed process descriptions, including parameters and return values. Processes are described using the Functio specification for language-agnostic process descriptions",
)
def view_process_all(db_session: Session = Depends(get_db)):
    process_records = service.get_process_all(db_session=db_session)
    if not process_records:
        raise HTTPException(status_code=404, detail=f"No processes have been created")
    response_data = {
        "processes": process_records,
        "links": [
            {
                "rel": "alternate",
                "href": "https://jeodpp.jrc.ec.europa.eu/services/openeo/processes",
                "type": "text/html",
                "title": "HTML version of the processes",
            },
        ],
    }
    return response_data


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
