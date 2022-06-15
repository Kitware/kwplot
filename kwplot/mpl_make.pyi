from typing import Dict
import kwimage
from nptyping import NDArray
from numpy import ndarray
import matplotlib
from typing import Union
from typing import Optional
import numpy as np
from _typeshed import Incomplete
from kwimage import make_heatmask as make_heatmask, make_orimask as make_orimask, make_vector_field as make_vector_field


def make_legend_img(label_to_color: Dict[str, kwimage.Color],
                    dpi: int = ...,
                    shape=...,
                    mode: str = ...,
                    transparent: bool = ...):
    ...


def crop_border_by_color(img: NDArray,
                         fillval: None = None,
                         thresh: int = 0,
                         channel: Incomplete | None = ...) -> ndarray:
    ...


def get_pixel_dist(img, pixel, channel: Incomplete | None = ...):
    ...


def render_figure_to_image(fig: matplotlib.figure.Figure,
                           dpi: Optional[Union[int, str]] = None,
                           transparent: bool = None,
                           **savekw) -> np.ndarray:
    ...
