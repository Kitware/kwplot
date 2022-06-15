from _typeshed import Incomplete


class PlotNums:
    nRows: Incomplete
    nCols: Incomplete
    offset: Incomplete
    start: Incomplete

    def __init__(self,
                 nRows: Incomplete | None = ...,
                 nCols: Incomplete | None = ...,
                 nSubplots: Incomplete | None = ...,
                 start: int = ...) -> None:
        ...

    def __getitem__(self, px):
        ...

    def __call__(self):
        ...

    def __iter__(self) -> tuple:
        ...

    def __len__(self):
        ...
