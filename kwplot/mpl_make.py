# -*- coding: utf-8 -*-
"""
DEPRECATED: use kwimage versions instead

Functions used to explicitly make images as ndarrays using mpl/cv2 utilities
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
from kwimage import make_heatmask, make_vector_field, make_orimask  # NOQA

__all__ = ['make_heatmask', 'make_vector_field', 'make_orimask', 'make_legend_img']


def make_legend_img(label_to_color, dpi=96, shape=(200, 200), mode='line',
                    transparent=False):
    """
    Makes an image of a categorical legend

    Args:
        label_to_color (Dict[str, Color]): mapping from string label to the
            color.

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
    import kwimage
    plt = kwplot.autoplt()

    def append_phantom_legend_label(label, color, type_='line', alpha=1.0, ax=None):
        if ax is None:
            ax = plt.gca()
        _phantom_legend_list = getattr(ax, '_phantom_legend_list', None)
        if _phantom_legend_list is None:
            _phantom_legend_list = []
            setattr(ax, '_phantom_legend_list', _phantom_legend_list)
        if type_ == 'line':
            phantom_actor = plt.Line2D((0, 0), (1, 1), color=color, label=label,
                                       alpha=alpha)
        else:
            phantom_actor = plt.Circle((0, 0), 1, fc=color, label=label,
                                       alpha=alpha)
        _phantom_legend_list.append(phantom_actor)

    fig = plt.figure(dpi=dpi)

    w, h = shape[1] / dpi, shape[0] / dpi
    fig.set_size_inches(w, h)

    # ax = fig.add_subplot('111')
    ax = fig.add_subplot(1, 1, 1)
    for label, color in label_to_color.items():
        color = kwimage.Color(color).as01()
        append_phantom_legend_label(label, color, type_=mode, ax=ax)

    _phantom_legend_list = getattr(ax, '_phantom_legend_list', None)
    if _phantom_legend_list is None:
        _phantom_legend_list = []
        setattr(ax, '_phantom_legend_list', _phantom_legend_list)
    ax.legend(handles=_phantom_legend_list)
    ax.grid(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.axis('off')
    legend_img = render_figure_to_image(fig, dpi=dpi, transparent=transparent)
    legend_img = kwimage.convert_colorspace(legend_img, src_space='bgr', dst_space='rgb')
    legend_img = crop_border_by_color(legend_img)

    plt.close(fig)
    return legend_img


def crop_border_by_color(img, fillval=None, thresh=0, channel=None):
    r"""
    Crops image to remove fillval

    Args:
        img (ndarray[uint8_t, ndim=2]):  image data
        fillval (None): (default = None)
        thresh (int): (default = 0)

    Returns:
        ndarray: cropped_img
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

        dpi (int or str, Optional):
            The resolution in dots per inch.  If *None* it will default to the
            value ``savefig.dpi`` in the matplotlibrc file.  If 'figure' it
            will set the dpi to be the value of the figure.

        transparent (bool):
            If *True*, the axes patches will all be transparent; the
            figure patch will also be transparent unless facecolor
            and/or edgecolor are specified via kwargs.

        **savekw: other keywords passed to `fig.savefig`. Valid keywords
            include: facecolor, edgecolor, orientation, papertype, format,
            pad_inches, frameon.

    Returns:
        np.ndarray: an image in BGR or BGRA format.

    Notes:
        Be sure to use `fig.set_size_inches` to an appropriate size before
        calling this function.
    """
    import io
    import cv2
    extent = 'tight'  # mpl might do this correctly these days
    with io.BytesIO() as stream:
        # This call takes 23% - 15% of the time depending on settings
        fig.savefig(stream, bbox_inches=extent, dpi=dpi,
                    transparent=transparent, **savekw)
        stream.seek(0)
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    im_bgra = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    return im_bgra
