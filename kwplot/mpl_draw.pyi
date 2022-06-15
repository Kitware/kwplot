import kwimage
from typing import List
from numpy import ndarray
from typing import Union
import pandas as pd
from _typeshed import Incomplete
from kwimage import draw_boxes_on_image as draw_boxes_on_image, draw_clf_on_image as draw_clf_on_image, draw_text_on_image as draw_text_on_image


def draw_boxes(boxes: kwimage.Boxes,
               alpha: List[float] = None,
               color: str = ...,
               labels: List[str] = None,
               centers: bool = False,
               fill: bool = ...,
               ax: Incomplete | None = ...,
               lw: float = 2) -> None:
    ...


def draw_line_segments(pts1: ndarray,
                       pts2: ndarray,
                       ax: None = None,
                       **kwargs) -> None:
    ...


def plot_matrix(matrix: Union[ndarray, pd.DataFrame],
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
