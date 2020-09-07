import json
import logging


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status


from . import service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", summary="Retrieve list of all collections")
def view_collection_all():
    collections = service.get_collection_all()
    if not collections:
        raise HTTPException(status_code=404, detail=f"No collections have been created")
    return collections


@router.get("/{collection_name}", summary="The request will ask the back-end for further details about a collection specified by the identifier collection_name")
def view_collection_detail(collection_name: str):
    collection = service.get_collection_by_id(collection_name)
    if not collection:
        raise HTTPException(status_code=404, detail=f"No collections with id {collection_name} have been created")
    return collection
