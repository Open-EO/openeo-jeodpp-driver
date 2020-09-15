import logging


from fastapi import FastAPI
from fastapi import Depends
from fastapi_utils.api_settings import get_api_settings
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .settings import get_settings
from .database import get_db

from . import collection
from . import process
from . import job


logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    # settings
    get_api_settings.cache_clear()
    api_settings = get_api_settings()
    settings = get_settings()
    # app
    app = FastAPI(**api_settings.fastapi_kwargs)
    # middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.fastapi_cors_origins.splitlines(),
        # allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # routes
    app.include_router(collection.router, prefix="/collections", tags=["collections"])
    app.include_router(process.router, prefix="/processes", tags=["processes"])
    app.include_router(job.router, prefix="/jobs", tags=["jobs"])
    return app


app = get_app()


@app.get("/healthcheck")
async def healthckeck():
    return {"healthcheck": "OK"}


@app.get("/db_connectivity")
def db_connectivity(db: Session = Depends(get_db)):
    db.execute("SELECT 1;")
    return {"db_connectivity": "OK"}
