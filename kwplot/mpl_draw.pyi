import kwimage
from typing import List
from typing import Any
import matplotlib
from numpy import ndarray
import pandas as pd
from _typeshed import Incomplete
from kwimage import draw_boxes_on_image as draw_boxes_on_image, draw_clf_on_image as draw_clf_on_image, draw_text_on_image as draw_text_on_image


def draw_boxes(boxes: kwimage.Boxes,
               alpha: float | List[float] | None = None,
               color: str | Any | List[Any] = 'blue',
               labels: List[str] | None = None,
               centers: bool = False,
               fill: bool = ...,
               ax: matplotlib.axes.Axes | None = None,
               lw: float = 2) -> None:
    ...


def draw_line_segments(pts1: ndarray,
                       pts2: ndarray,
                       ax: None = None,
                       **kwargs) -> None:
    ...


def plot_matrix(matrix: ndarray | pd.DataFrame,
                index: Incomplete | None = ...,
                columns: Incomplete | None = ...,
                rot: int = ...,
                ax: Incomplete | None = ...,
                grid: bool = ...,
                label: Incomplete | None = ...,
                zerodiag: bool = ...,
                cmap: str = ...,
                showvals: bool = ...,
                showzero: bool = ...,
                logscale: bool = ...,
                xlabel: Incomplete | None = ...,
                ylabel: Incomplete | None = ...,
                fnum: Incomplete | None = ...,
                pnum: Incomplete | None = ...):
    ...


def draw_points(xy: ndarray,
                color: str = ...,
                class_idxs: Incomplete | None = ...,
                classes: Incomplete | None = ...,
                ax: Incomplete | None = ...,
                alpha: Incomplete | None = ...,
                radius: int = ...,
                **kwargs):
    ...
