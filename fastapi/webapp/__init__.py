import logging


from fastapi import FastAPI
from fastapi_utils.api_settings import get_api_settings
from fastapi.middleware.cors import CORSMiddleware


from .settings import get_settings
from . import collection
from . import process

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    # settings
    get_api_settings.cache_clear()
    api_settings = get_api_settings()
    # settings = get_settings()
    # app
    app = FastAPI(**api_settings.fastapi_kwargs)
    # middleware
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=settings.backend_cors_origins.splitlines(),
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # routes
    app.include_router(collection.router, prefix="/collections", tags=["collections"])
    app.include_router(process.router, prefix="/processes", tags=["processes"])
    return app


app = get_app()
