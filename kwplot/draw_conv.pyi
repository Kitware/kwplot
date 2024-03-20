import torch
import torch.nn
from numpy import ndarray
import matplotlib
from _typeshed import Incomplete


def make_conv_images(conv: torch.nn.Conv2d | ndarray,
                     color: bool | None = None,
                     norm_per_feat: bool = True) -> ndarray:
    ...


def plot_convolutional_features(
        conv: torch.nn.modules.conv._ConvNd,
        limit: int = 144,
        colorspace: str = 'rgb',
        fnum: Incomplete | None = ...,
        nCols: Incomplete | None = ...,
        voxels: bool = False,
        alpha: float = 0.2,
        labels: bool = ...,
        normaxis: Incomplete | None = ...,
        _hack_2drows: bool = ...) -> matplotlib.figure.Figure:
    ...
