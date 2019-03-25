# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ubelt as ub
import pandas as pd
import copy
import numpy as np


def draw_boxes(boxes, alpha=None, color='blue', labels=None, centers=False,
               fill=False, ax=None, lw=2):
    """
    Args:
        labels (List[str]): of labels
        alpha (List[float]): alpha for each box
        centers (bool): draw centers or not
        lw (float): linewidth

    Example:
        >>> import kwimage
        >>> bboxes = kwimage.Boxes([[.1, .1, .6, .3], [.3, .5, .5, .6]], 'xywh')
        >>> draw_boxes(bboxes)
        >>> #kwplot.autompl()
    """
    import kwplot
    import matplotlib as mpl
    from matplotlib import pyplot as plt
    if ax is None:
        ax = plt.gca()

    xywh = boxes.to_xywh().data

    transparent = kwplot.Color((0, 0, 0, 0)).as01('rgba')

    # More grouped patches == more efficient runtime
    if alpha is None:
        alpha = [1.0] * len(xywh)
    elif not ub.iterable(alpha):
        alpha = [alpha] * len(xywh)

    edgecolors = [kwplot.Color(color, alpha=a).as01('rgba')
                  for a in alpha]
    color_groups = ub.group_items(range(len(edgecolors)), edgecolors)
    for edgecolor, idxs in color_groups.items():
        if fill:
            fc = edgecolor
        else:
            fc = transparent
        rectkw = dict(ec=edgecolor, fc=fc, lw=lw, linestyle='solid')
        patches = [mpl.patches.Rectangle((x, y), w, h, **rectkw)
                   for x, y, w, h in xywh[idxs]]
        col = mpl.collections.PatchCollection(patches, match_original=True)
        ax.add_collection(col)

    if centers not in [None, False]:
        default_centerkw = {
            'radius': 1,
            'fill': True
        }
        centerkw = default_centerkw.copy()
        if isinstance(centers, dict):
            centerkw.update(centers)
        xy_centers = boxes.xy_center
        for fcolor, idxs in color_groups.items():
            patches = [
                mpl.patches.Circle((x, y), ec=None, fc=fcolor, **centerkw)
                for x, y in xy_centers[idxs]
            ]
            col = mpl.collections.PatchCollection(patches, match_original=True)
            ax.add_collection(col)

    if labels:
        texts = []
        default_textkw = {
            'horizontalalignment': 'left',
            'verticalalignment': 'top',
            'backgroundcolor': (0, 0, 0, .8),
            'color': 'white',
            'fontproperties': mpl.font_manager.FontProperties(
                size=6, family='monospace'),
        }
        tkw = default_textkw.copy()
        for (x1, y1, w, h), label in zip(xywh, labels):
            texts.append((x1, y1, label, tkw))
        for (x1, y1, catname, tkw) in texts:
            ax.text(x1, y1, catname, **tkw)


def draw_line_segments(pts1, pts2, ax=None, **kwargs):
    """
    draws `N` line segments between `N` pairs of points

    Args:
        pts1 (ndarray): Nx2
        pts2 (ndarray): Nx2
        ax (None): (default = None)
        **kwargs: lw, alpha, colors

    Example:
        >>> import numpy as np
        >>> import kwplot
        >>> pts1 = np.array([(.1, .8), (.6, .8)])
        >>> pts2 = np.array([(.6, .7), (.4, .1)])
        >>> kwplot.figure(fnum=None)
        >>> draw_line_segments(pts1, pts2)
        >>> # xdoc: +REQUIRES(--show)
        >>> import matplotlib.pyplot as plt
        >>> ax = plt.gca()
        >>> ax.set_xlim(0, 1)
        >>> ax.set_ylim(0, 1)
        >>> kwplot.show_if_requested()
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    if ax is None:
        ax = plt.gca()
    assert len(pts1) == len(pts2), 'unaligned'
    segments = [(xy1, xy2) for xy1, xy2 in zip(pts1, pts2)]
    linewidth = kwargs.pop('lw', kwargs.pop('linewidth', 1.0))
    alpha = kwargs.pop('alpha', 1.0)
    if 'color' in kwargs:
        kwargs['colors'] = kwargs['color']
        # mpl.colors.ColorConverter().to_rgb(kwargs['color'])
    line_group = mpl.collections.LineCollection(segments, linewidths=linewidth,
                                                alpha=alpha, **kwargs)
    ax.add_collection(line_group)


def plot_matrix(matrix, index=None, columns=None, rot=90, ax=None, grid=True,
                label=None, zerodiag=False, cmap='viridis', showvals=False,
                showzero=True, logscale=False, xlabel=None, ylabel=None):
    """
    Helper for plotting confusion matrices

    Args:
        matrix (ndarray | pd.DataFrame) : if a data frame then index, columns,
            xlabel, and ylabel will be defaulted to sensible values.

    TODO:
        - [ ] Finish args docs
        - [ ] Replace internals with seaborn

    Example:
        >>> classes = ['cls1', 'cls2', 'cls3']
        >>> matrix = np.array([[2, 2, 1], [3, 1, 0], [1, 0, 0]])
        >>> matrix = pd.DataFrame(matrix, index=classes, columns=classes)
        >>> matrix.index.name = 'real'
        >>> matrix.columns.name = 'pred'
        >>> plot_matrix(matrix, showvals=True)
    """
    import matplotlib as mpl
    from matplotlib import pyplot as plt
    import matplotlib.cm  # NOQA

    assert len(matrix.shape) == 2

    if isinstance(matrix, pd.DataFrame):
        values = matrix.values
        if index is None and columns is None:
            index = matrix.index
            columns = matrix.columns
            if xlabel is None and ylabel is None:
                ylabel = index.name
                xlabel = columns.name
    else:
        values = matrix

    if index is None:
        index = np.arange(len(matrix))

    if columns is None:
        index = np.arange(matrix)

    if ax is None:
        fig = plt.gcf()
        # figure(fnum=1, pnum=(1, 1, 1))
        fig.clear()
        ax = plt.gca()
    ax = plt.gca()
    if zerodiag:
        values = values.copy()
        values = values - np.diag(np.diag(values))

    # aximg = ax.imshow(values, interpolation='none', cmap='viridis')
    if logscale:
        from matplotlib.colors import LogNorm
        vmin = values[values > 0].min().min()
        norm = LogNorm(vmin=vmin, vmax=values.max())
    else:
        norm = None

    cmap = copy.copy(mpl.cm.get_cmap(cmap))  # copy the default cmap
    cmap.set_bad((0, 0, 0))

    if not showzero and not logscale:
        # hack zero to be black
        cmap.colors[0] = [0, 0, 0]

    aximg = ax.matshow(values, interpolation='none', cmap=cmap, norm=norm)

    ax.grid(False)
    cax = plt.colorbar(aximg, ax=ax)
    if label is not None:
        cax.set_label(label)

    ax.set_xticks(list(range(len(index))))
    ax.set_xticklabels([lbl[0:100] for lbl in index])
    for lbl in ax.get_xticklabels():
        lbl.set_rotation(rot)
    for lbl in ax.get_xticklabels():
        lbl.set_horizontalalignment('center')

    ax.set_yticks(list(range(len(columns))))
    ax.set_yticklabels([lbl[0:100] for lbl in columns])
    for lbl in ax.get_yticklabels():
        lbl.set_horizontalalignment('right')
    for lbl in ax.get_yticklabels():
        lbl.set_verticalalignment('center')

    # Grid lines around the pixels
    if grid:
        offset = -.5
        xlim = [-.5, len(columns)]
        ylim = [-.5, len(index)]
        segments = []
        for x in range(ylim[1]):
            xdata = [x + offset, x + offset]
            ydata = ylim
            segment = list(zip(xdata, ydata))
            segments.append(segment)
        for y in range(xlim[1]):
            xdata = xlim
            ydata = [y + offset, y + offset]
            segment = list(zip(xdata, ydata))
            segments.append(segment)
        bingrid = mpl.collections.LineCollection(segments, color='w', linewidths=1)
        ax.add_collection(bingrid)

    if showvals:
        x_basis = np.arange(len(columns))
        y_basis = np.arange(len(index))
        x, y = np.meshgrid(x_basis, y_basis)

        for c, r in zip(x.flatten(), y.flatten()):
            val = values[r, c]
            if val == 0:
                if showzero:
                    ax.text(c, r, val, va='center', ha='center', color='white')
            else:
                ax.text(c, r, val, va='center', ha='center', color='white')

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if ylabel is not None:
        ax.set_ylabel(ylabel)
    return ax


def draw_clf_on_image(im, classes, tcx, probs=None, pcx=None, border=1):
    """
    Draws classification label on an image

    Args:
        im (ndarray): the image
        classes (Sequence): list of class names
        tcx (int): true class index
        probs (int): predicted class probs
        pcx (int): predicted class index. (if none finds argmax of probs)

    Example:
        >>> import torch
        >>> import kwarray
        >>> import kwplot
        >>> rng = kwarray.ensure_rng(0)
        >>> im = (rng.rand(300, 300) * 255).astype(np.uint8)
        >>> classes = ['cls_a', 'cls_b', 'cls_c']
        >>> tcx = 1
        >>> probs = rng.rand(len(classes))
        >>> probs[tcx] = 0
        >>> probs = torch.FloatTensor(probs).softmax(dim=0).numpy()
        >>> im1_ = kwplot.draw_clf_on_image(im, classes, tcx, probs)
        >>> probs[tcx] = .9
        >>> probs = torch.FloatTensor(probs).softmax(dim=0).numpy()
        >>> im2_ = kwplot.draw_clf_on_image(im, classes, tcx, probs)
        >>> # xdoctest: +REQUIRES(--show)
        >>> kwplot.autompl()
        >>> kwplot.imshow(im1_, colorspace='rgb', pnum=(1, 2, 1), fnum=1, doclf=True)
        >>> kwplot.imshow(im2_, colorspace='rgb', pnum=(1, 2, 2), fnum=1)
        >>> kwplot.show_if_requested()
    """
    import kwimage
    im_ = kwimage.atleast_3channels(im)
    h, w = im.shape[0:2][::-1]

    if pcx is None and probs is not None:
        pcx = probs.argmax()
    else:
        pcx = None

    if probs is not None:
        pred_score = probs[pcx]
        true_score = probs[tcx]

    org1 = np.array((2, h - 5))
    org2 = np.array((2, 5))

    true_name = classes[tcx]
    if pcx == tcx:
        true_label = 't:{tcx}:{true_name}'.format(**locals())
    elif probs is None:
        true_label = 't:{tcx}:\n{true_name}'.format(**locals())
    else:
        true_label = 't:{tcx}@{true_score:.2f}:\n{true_name}'.format(**locals())

    pred_label = None
    if pcx is not None:
        pred_name = classes[pcx]
        if probs is None:
            pred_label = 'p:{pcx}:\n{pred_name}'.format(**locals())
        else:
            pred_label = 'p:{pcx}@{pred_score:.2f}:\n{pred_name}'.format(**locals())

    fontkw = {
        'fontScale': 1.0,
        'thickness': 2
    }
    color = 'dodgerblue' if pcx == tcx else 'orangered'

    from kwimage import draw_text_on_image
    # im_ = draw_text_on_image(im_, pred_label, org=org1 - 2,
    #                                  color='white', valign='bottom', **fontkw)
    # im_ = draw_text_on_image(im_, true_label, org=org2 - 2,
    #                                  color='white', valign='top', **fontkw)

    if pred_label is not None:
        im_ = draw_text_on_image(im_, pred_label, org=org1, color=color,
                                 border=border, valign='bottom', **fontkw)
    im_ = draw_text_on_image(im_, true_label, org=org2, color='lawngreen',
                             valign='top', border=border, **fontkw)
    return im_
