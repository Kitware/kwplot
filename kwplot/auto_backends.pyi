from types import ModuleType
from _typeshed import Incomplete


def set_mpl_backend(backend: str, verbose: Incomplete | None = ...) -> None:
    ...


def autompl(verbose: int = 0,
            recheck: bool = False,
            force: str = None) -> None:
    ...


def autoplt(verbose: int = ...,
            recheck: bool = ...,
            force: Incomplete | None = ...) -> ModuleType:
    ...


def autosns(verbose: int = ...,
            recheck: bool = ...,
            force: Incomplete | None = ...) -> ModuleType:
    ...


class BackendContext:
    backend: Incomplete
    prev: Incomplete

    def __init__(self, backend) -> None:
        ...

    def __enter__(self) -> None:
        ...

    def __exit__(self, *args) -> None:
        ...
