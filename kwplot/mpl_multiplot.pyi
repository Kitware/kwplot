from typing import Dict
from typing import List
from numpy import ndarray
from typing import Tuple
import matplotlib


def multi_plot(xdata: List[ndarray] | Dict[str, ndarray] | ndarray
               | None = None,
               ydata: List[ndarray] | Dict[str, ndarray] | ndarray
               | None = None,
               xydata: Dict[str, Tuple[ndarray, ndarray]] | None = None,
               **kwargs) -> matplotlib.axes.Axes:
    ...


def is_listlike(data):
    ...


def is_list_of_scalars(data):
    ...


def is_list_of_lists(data):
    ...
