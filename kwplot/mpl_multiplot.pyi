from typing import Union
from typing import Dict
from typing import List
from numpy import ndarray
from typing import Tuple
import matplotlib


def multi_plot(xdata: Union[List[ndarray], Dict[str, ndarray], ndarray] = None,
               ydata: Union[List[ndarray], Dict[str, ndarray], ndarray] = None,
               xydata: Dict[str, Tuple[ndarray, ndarray]] = None,
               **kwargs) -> matplotlib.axes.Axes:
    ...


def is_listlike(data):
    ...


def is_list_of_scalars(data):
    ...


def is_list_of_lists(data):
    ...
