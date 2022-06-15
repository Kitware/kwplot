# -*- coding: utf-8 -*-
"""
DEPRECATED: use kwimage versions instead

Functions used to explicitly make images as ndarrays using mpl/cv2 utilities
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
from kwimage import make_heatmask, make_vector_field, make_orimask  # NOQA

__all__ = [
    'make_heatmask', 'make_vector_field', 'make_orimask', 'make_legend_img',
    'render_figure_to_image',
]


def make_legend_img(label_to_color, dpi=96, shape=(200, 200), mode='line',
                    transparent=False):
    """
    Makes an image of a categorical legend

    Args:
        label_to_color (Dict[str, kwimage.Color]):
            mapping from string label to the color.

    CommandLine:
        xdoctest -m kwplot.mpl_make make_legend_img --show

    Example:
        >>> # xdoctest: +REQUIRES(module:kwplot)
        >>> import kwplot
        >>> import kwimage
        >>> label_to_color = {
        >>>     'blue': kwimage.Color('blue').as01(),
        >>>     'red': kwimage.Color('red').as01(),
        >>>     'green': 'green',
        >>>     'yellow': 'yellow',
        >>>     'orangered': 'orangered',
        >>> }
        >>> img = make_legend_img(label_to_color, transparent=True)
        >>> # xdoctest: +REQUIRES(--show)
        >>> kwplot.autompl()
        >>> kwplot.imshow(img)
        >>> kwplot.show_if_requested()
    """
    import kwplot
    plt = kwplot.autoplt()

    fig = plt.figure(dpi=dpi)

    w, h = shape[1] / dpi, shape[0] / dpi
    fig.set_size_inches(w, h)

    # ax = fig.add_subplot('111')
    ax = fig.add_subplot(1, 1, 1)
    kwplot.phantom_legend(label_to_color, mode=mode, ax=ax)
    ax.grid(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.axis('off')
    legend_img = render_figure_to_image(fig, dpi=dpi, transparent=transparent)
    legend_img = crop_border_by_color(legend_img)

    plt.close(fig)
    return legend_img


def crop_border_by_color(img, fillval=None, thresh=0, channel=None):
    r"""
    Crops image to remove any constant color padding.

    Args:
        img (NDArray):
            image data

        fillval (None):
            The color to replace.
            Defaults "white" (i.e. `(255,) * num_channels`)

        thresh (int):
            Allowable difference to `fillval` (default = 0)

    Returns:
        ndarray: cropped_img

    TODO:
        does this belong in kwimage?
    """
    import kwimage
    if fillval is None:
        fillval = np.array([255] * kwimage.num_channels(img))
    # for colored images
    #with ut.embed_on_exception_context:
    pixel = fillval
    dist = get_pixel_dist(img, pixel, channel=channel)
    isfill = dist <= thresh
    # isfill should just be 2D
    # Fix shape that comes back as (1, W, H)
    if len(isfill.shape) == 3 and isfill.shape[0] == 1:
        if np.all(np.greater(isfill.shape[1:2], [4, 4])):
            isfill = isfill[0]
    rowslice, colslice = _get_crop_slices(isfill)
    cropped_img = img[rowslice, colslice]
    return cropped_img


def _get_crop_slices(isfill):
    import kwarray
    fill_colxs = [np.where(row)[0] for row in isfill]
    fill_rowxs = [np.where(col)[0] for col in isfill.T]
    nRows, nCols = isfill.shape[0:2]
    from functools import reduce
    filled_columns = reduce(np.intersect1d, fill_colxs)
    filled_rows = reduce(np.intersect1d, fill_rowxs)

    consec_rows_list = kwarray.group_consecutive(filled_rows)
    consec_cols_list = kwarray.group_consecutive(filled_columns)

    def get_consec_endpoint(consec_index_list, endpoint):
        """
        consec_index_list = consec_cols_list
        endpoint = 0
        """
        for consec_index in consec_index_list:
            if np.any(np.array(consec_index) == endpoint):
                return consec_index

    def get_min_consec_endpoint(consec_rows_list, endpoint):
        consec_index = get_consec_endpoint(consec_rows_list, endpoint)
        if consec_index is None:
            return endpoint
        return max(consec_index)

    def get_max_consec_endpoint(consec_rows_list, endpoint):
        consec_index = get_consec_endpoint(consec_rows_list, endpoint)
        if consec_index is None:
            return endpoint + 1
        return min(consec_index)

    consec_rows_top    = get_min_consec_endpoint(consec_rows_list, 0)
    consec_rows_bottom = get_max_consec_endpoint(consec_rows_list, nRows - 1)
    remove_cols_left   = get_min_consec_endpoint(consec_cols_list, 0)
    remove_cols_right  = get_max_consec_endpoint(consec_cols_list, nCols - 1)
    rowslice = slice(consec_rows_top, consec_rows_bottom)
    colslice = slice(remove_cols_left, remove_cols_right)
    return rowslice, colslice


def get_pixel_dist(img, pixel, channel=None):
    """
    Example:
        >>> img = np.random.rand(256, 256, 3)
        >>> pixel = np.random.rand(3)
        >>> channel = None
        >>> get_pixel_dist(img, pixel, channel)
    """
    import kwimage
    pixel = np.asarray(pixel)
    if len(pixel.shape) < 2:
        pixel = pixel[None, None, :]
    img, pixel = kwimage.make_channels_comparable(img, pixel)
    dist = np.abs(img - pixel)
    if len(img.shape) > 2:
        if channel is None:
            dist = np.sum(dist, axis=2)
        else:
            dist = dist[:, :, channel]
    return dist


def render_figure_to_image(fig, dpi=None, transparent=None, **savekw):
    """
    Saves a figure as an image in memory.

    Args:
        fig (matplotlib.figure.Figure): figure to save

        dpi (Optional[int | str]):
            The resolution in dots per inch.  If *None* it will default to the
            value ``savefig.dpi`` in the matplotlibrc file.  If 'figure' it
            will set the dpi to be the value of the figure.

        transparent (bool):
            If *True*, the axes patches will all be transparent; the
            figure patch will also be transparent unless facecolor
            and/or edgecolor are specified via kwargs.

        **savekw: other keywords passed to ``fig.savefig``. Valid keywords
            include: facecolor, edgecolor, orientation, papertype, format,
            pad_inches, frameon.

    Returns:
        np.ndarray: an image in RGB or RGBA format.

    Note:
        Be sure to use `fig.set_size_inches` to an appropriate size before
        calling this function.

    Example:
        >>> import kwplot
        >>> fig = kwplot.figure(fnum=1, doclf=True)
        >>> ax = fig.gca()
        >>> ax.cla()
        >>> ax.plot([0, 10], [0, 10])
        >>> canvas_rgb = kwplot.render_figure_to_image(fig, transparent=False)
        >>> canvas_rgba = kwplot.render_figure_to_image(fig, transparent=True)
        >>> assert canvas_rgb.shape[2] == 3
        >>> assert canvas_rgba.shape[2] == 4
        >>> # xdoctest: +REQUIRES(--show)
        >>> kwplot.autompl()
        >>> kwplot.imshow(canvas_rgb, fnum=2)
        >>> kwplot.show_if_requested()
    """
    import io
    import cv2
    import kwimage
    extent = 'tight'  # mpl might do this correctly these days
    with io.BytesIO() as stream:
        # This call takes 23% - 15% of the time depending on settings
        fig.savefig(stream, bbox_inches=extent, dpi=dpi,
                    transparent=transparent, **savekw)
        stream.seek(0)
        data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    im_bgra = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if transparent is not None and not transparent:
        im_rgba = kwimage.convert_colorspace(im_bgra, src_space='bgra', dst_space='rgb')
    else:
        im_rgba = kwimage.convert_colorspace(im_bgra, src_space='bgra', dst_space='rgba')
    return im_rgba
