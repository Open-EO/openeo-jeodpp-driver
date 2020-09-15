import json
import logging


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
import psycopg2.errors
import sqlalchemy.exc


from . import service
from .. import models
from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=models.ViewCollectionAll,
    summary="Retrieve list of all collections",
)
def view_collection_all(db_session: Session = Depends(get_db)):
    collections = service.get_collection_all(db_session=db_session)
    if not collections:
        raise HTTPException(
            status_code=404,
            detail=f"Requests will ask the back-end for available collections and will return an array of available collections with very basic information such as their unique identifiers.",
        )
    return collections


@router.get(
    "/{collection_id}",
    response_model=models.CollectionBase,
    summary="The request will ask the back-end for further details about a collection specified by the identifier collection_name",
)
def view_collection_detail(collection_id: str, db_session: Session = Depends(get_db)):
    collection = service.get_collection_by_id(
        collection_id=collection_id, db_session=db_session
    )
    if not collection:
        raise HTTPException(
            status_code=404,
            detail=f"No collections with id {collection_id} have been created",
        )
    return collection


@router.post(
    "/",
    response_model=models.CollectionViewJeodpp,
    summary="Create a new collection record",
    status_code=status.HTTP_201_CREATED,
)
def create_collection_record(
    collection_record_in: models.CollectionBase, db_session: Session = Depends(get_db)
):
    try:
        collection_record = service.create(
            db_session=db_session, collection_record_in=collection_record_in
        )
    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InternalError) as exc:
        if isinstance(exc.orig, psycopg2.errors.UniqueViolation):
            msg = f"A collection record with the collection_id {collection_record_in.collection_id} already exists"
        else:
            msg = "Creation of Collection failed. Please check the logs."
        raise HTTPException(status_code=422, detail=msg)
    return collection_record


@router.delete("/", summary="Remove collection", status_code=status.HTTP_204_NO_CONTENT)
def remove_collection_record(collection_id: str, db_session: Session = Depends(get_db)):
    try:
        deleted_collection_id = service.delete(
            db_session=db_session, collection_id=collection_id
        )
    except sqlalchemy.exc.IntegrityError as exc:
        raise HTTPException(status_code=422, detail=exc)
