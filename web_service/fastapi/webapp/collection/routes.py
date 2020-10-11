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
    "",
    response_model=models.ViewCollectionAllOpeneo,
    summary="Retrieve list of all collections",
)
def view_collection_all(db_session: Session = Depends(get_db)):
    collection_records = service.get_collection_all_openeo(db_session=db_session)
    if not collection_records:
        raise HTTPException(
            status_code=404,
            detail=f"Requests will ask the back-end for available collections and will return an array of available collections with very basic information such as their unique identifiers.",
        )
    response_data = {
        "collections": collection_records,
        "links": [
            {
                "rel": "string",
                "href": "https://jeodpp.jrc.ec.europa.eu/services/openeo/collections",
                "type": "string",
                "title": "string",
            },
            {
                "rel": "alternate",
                "href": "https://jeodpp.jrc.ec.europa.eu/services/csw",
                "title": "openEO catalog (OGC Catalogue Services 3.0)",
            },
        ],
    }
    return response_data


@router.get(
    "/bda",
    response_model=models.ViewCollectionAll,
    summary="Retrieve list of all bda collections",
)
def view_collection_all(db_session: Session = Depends(get_db)):
    collection_records = service.get_collection_all(db_session=db_session)
    if not collection_records:
        raise HTTPException(
            status_code=404,
            detail=f"Requests will ask the back-end for available collections and will return an array of available collections with very basic information such as their unique identifiers.",
        )
    response_data = {"collections": collection_records}
    return response_data


@router.get(
    "/{collection_id}",
    response_model=models.StacCollectionMetadata,
    summary="The request will ask the back-end for further details about a collection specified by the identifier collection_name",
)
def view_collection_detail(collection_id: str, db_session: Session = Depends(get_db)):
    collection = service.get_collection_by_id_openeo(
        collection_id=collection_id, db_session=db_session
    )
    if not collection:
        raise HTTPException(
            status_code=404,
            detail=f"No collections with id {collection_id} have been created",
        )
    return collection


@router.get(
    "/{collection_id}/bda",
    response_model=models.CollectionViewJeodpp,
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


@router.put(
    "/",
    response_model=models.CollectionViewJeodpp,
    summary="Update existing collection record",
)
def update_collection_record(
    collection_id: str,
    collection_record_update: models.CollectionBase,
    db_session: Session = Depends(get_db),
):
    try:
        updated_collection_record = service.update(
            db_session=db_session,
            collection_id=collection_id,
            collection_record_update=collection_record_update,
        )
    except sqlalchemy.exc.IntegrityError as exc:
        raise HTTPException(status_code=422, detail=exc)
    else:
        return updated_collection_record


@router.delete("/", summary="Remove collection", status_code=status.HTTP_204_NO_CONTENT)
def remove_collection_record(collection_id: str, db_session: Session = Depends(get_db)):
    try:
        deleted_collection_id = service.delete(
            db_session=db_session, collection_id=collection_id
        )
    except sqlalchemy.exc.IntegrityError as exc:
        raise HTTPException(status_code=422, detail=exc)
