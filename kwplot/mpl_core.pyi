import matplotlib as mpl
from numpy import ndarray
from typing import List
from typing import Tuple
from typing import Dict
import kwimage
from typing import Any
from _typeshed import Incomplete


def next_fnum(new_base: Incomplete | None = ...):
    ...


def ensure_fnum(fnum):
    ...


def figure(fnum: int | None = None,
           pnum=...,
           title: str | None = None,
           figtitle: None = None,
           doclf: bool = False,
           docla: bool = False,
           projection: Incomplete | None = ...,
           **kwargs) -> mpl.figure.Figure:
    ...


def legend(loc: str = 'best',
           fontproperties: None = None,
           size: None = None,
           fc: str = ...,
           alpha: int = ...,
           ax: Incomplete | None = ...,
           handles: Incomplete | None = ...) -> None:
    ...


def show_if_requested(N: int = ...) -> None:
    ...


def imshow(img: ndarray,
           fnum: int | None = None,
           pnum: tuple | None = None,
           xlabel: str | None = None,
           title: str | None = None,
           figtitle: str | None = None,
           ax: mpl.axes.Axes | None = None,
           norm: bool | None = None,
           cmap: mpl.colors.Colormap | None = None,
           data_colorbar: bool = False,
           colorspace: str = 'rgb',
           interpolation: str = 'nearest',
           alpha: Incomplete | None = ...,
           show_ticks: bool = ...,
           **kwargs) -> tuple:
    ...


def set_figtitle(figtitle: str,
                 subtitle: str = '',
                 forcefignum: bool = True,
                 incanvas: bool = True,
                 size: None = None,
                 fontfamily: None = None,
                 fontweight: None = None,
                 fig: None = None) -> None:
    ...


def distinct_markers(num: int,
                     style: str = 'astrisk',
                     total: int | None = None,
                     offset: float = 0) -> List[Tuple]:
    ...


def distinct_colors(N: int,
                    brightness: float = 0.878,
                    randomize: bool = ...,
                    hue_range=...,
                    cmap_seed: Incomplete | None = ...) -> list:
    ...


def phantom_legend(label_to_color: Dict[str, kwimage.Color] | None = None,
                   label_to_attrs: Dict[str, Dict[str, Any]] | None = None,
                   mode: str = ...,
                   ax: Incomplete | None = ...,
                   legend_id: Incomplete | None = ...,
                   loc: int = ...) -> None:
    ...


def close_figures(figures: List[mpl.figure.Figure] | None = None) -> None:
    ...


def all_figures() -> List[mpl.figure.Figure]:
    ...
