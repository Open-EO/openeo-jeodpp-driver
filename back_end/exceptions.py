class BackendError(Exception):
    """Base class for Backend exceptions."""

    pass


class NoSuchProcess(BackendError):
    """Exception class for when process is not implemneted."""

    pass

