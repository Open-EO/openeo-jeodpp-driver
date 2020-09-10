import functools
import logging
import os

from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """ Parses variables from environment on instantiation """

    deploy_env: str
    backend_cors_origins: str

    db_host: str
    db_port: int
    postgres_db: str
    db_rpi_user: str
    db_rpi_pass: str

    testing: bool = False

    @property
    def db_uri(self):
        uri = (
            "postgresql://{db_rpi_user}:{db_rpi_pass}@{db_host}:{db_port}/{postgres_db}"
        )
        uri = uri.format(**self.__dict__)
        return uri

    postgres_user: str
    postgres_password: str

    @property
    def db_super_uri(self) -> str:
        uri = "postgresql://{postgres_user}:{postgres_password}@{db_host}:{db_port}/{postgres_db}"
        uri = uri.format(**self.__dict__)
        return uri

    @property
    def db_uri_test(self) -> str:
        uri = "postgresql://{db_rpi_user}:{db_rpi_pass}@{db_host}:{db_port}/{postgres_db}_test"
        uri = uri.format(**self.__dict__)
        return uri

    @property
    def db_super_uri_test(self) -> str:
        uri = "postgresql://{postgres_user}:{postgres_password}@{db_host}:{db_port}/{postgres_db}_test"
        uri = uri.format(**self.__dict__)
        return uri

    @property
    def db_super_uri_postgres(self) -> str:
        uri = "postgresql://{postgres_user}:{postgres_password}@{db_host}:{db_port}/postgres"
        uri = uri.format(**self.__dict__)
        return uri


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    return settings
