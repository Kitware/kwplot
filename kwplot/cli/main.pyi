from _typeshed import Incomplete
from scriptconfig import DataConfig

modal: Incomplete


class ImshowCLI(DataConfig):
    __command__: str
    fpath: Incomplete
    robust: Incomplete
    stats: Incomplete

    @classmethod
    def main(cls, cmdline: bool = ..., **kwargs) -> None:
        ...


def main() -> None:
    ...
