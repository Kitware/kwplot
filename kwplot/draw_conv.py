# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import ubelt as ub
try:
    import torch  # NOQA
except ImportError:
    print('warning: torch not available')
    torch = None


def make_conv_images(conv, color=None, norm_per_feat=True):
    """
    Convert convolutional weights to a list of visualize-able images

    Args:
        conv (Conv2d)
        color (bool): if True output images are colorized
        norm_per_feat (bool): if True normalizes over each feature separately,
            otherwise normalizes all features together.

    Returns:
        ndarray:

    TODO:
        - [ ] better normalization options

    Example:
        >>> # xdoctest: +REQUIRES(module:torch)
        >>> conv = torch.nn.Conv2d(3, 9, (5, 7))
        >>> weights_tohack = conv.weight[0:7].data.numpy()
        >>> weights_flat = make_conv_images(conv, norm_per_feat=False)
        >>> # xdoctest: +REQUIRES(--show)
        >>> import kwimage
        >>> import kwplot
        >>> stacked = kwimage.stack_images_grid(weights_flat, chunksize=5, overlap=-1)
        >>> kwplot.imshow(stacked)
        >>> kwplot.show_if_requested()

    Ignore:
        >>> # xdoctest: +REQUIRES(module:torch)
        >>> import torchvision
        >>> conv = torchvision.models.resnet50(pretrained=True).conv1
        >>> #conv = torchvision.models.vgg11(pretrained=True).features[0]
        >>> weights_flat = make_conv_images(conv, norm_per_feat=False)
        >>> # xdoctest: +REQUIRES(--show)
        >>> import kwplot
        >>> import kwimage
        >>> stacked = kwplot.stack_images_grid(weights_flat, chunksize=8, overlap=-1)
        >>> kwplot.autompl()
        >>> kwplot.imshow(stacked)
        >>> kwplotwil.show_if_requested()
    """
    # get relavent data out of pytorch module
    weights = conv.weight.data.cpu().numpy()
    in_channels = conv.in_channels
    # out_channels = conv.out_channels
    spatial_dims = list(conv.kernel_size)
    n_space_dims = len(spatial_dims)

    if color is None:
        # color if possible
        color = (in_channels == 3)

    # Normalize layer weights between 0 and 1
    if norm_per_feat:
        # if normaxis=0 norm over output channels
        minval = weights.min(axis=(0, 1), keepdims=True)
        maxval = weights.max(axis=(0, 1), keepdims=True)
    else:
        minval = weights.min()
        maxval = weights.max()

    weights_norm = (weights - minval) / (maxval - minval)

    # If there are 3 input channels, we can visualize features in a colorspace
    if color:
        # Move colorable channels to the end (handle 1, 2 and 3d convolution)
        ifeat_axes = [0]
        color_axes = [1]
        space_axes = list(range(2, 2 + n_space_dims))
        axes = ifeat_axes + space_axes + color_axes
        weights_norm = weights_norm.transpose(*axes)
        color_dims = [in_channels]
    else:
        color_dims = []

    # flatten all non-spacetime/color dimensions
    weights_flat = weights_norm.reshape(-1, *(spatial_dims + color_dims))
    return weights_flat


def plot_convolutional_features(conv, limit=144, colorspace='rgb', fnum=None,
                                nCols=None, voxels=False, alpha=.2,
                                labels=False, normaxis=None, _hack_2drows=False):
    """Plots the convolutional layers to a matplotlib pyplot.

    The convolutional filters (kernels) are stored into a grid and saved to disk
    as a Maplotlib figure.  The convolutional filters, if it has one channel,
    will be stored as an intensity imgage.  If a colorspace is specified and
    there are three input channels, the convolutional filters will be
    represented as an RGB image.

    In the event that 2 or 4+ filters are
    displayed, the different channels will be flattened and showed as distinct
    outputs in the grid.

    TODO:
        - [ ] refactor to use make_conv_images

    Args:
        conv (torch.nn.ConvNd): torch convolutional layer with weights to draw
        limit (int, optional): the limit on the number of filters drawn in the
            figure, achieved by simply dropping any filters past the limit
            starting at the first filter.  Detaults to 144.

        colorspace (str): the colorspace seen by the convolutional filter
            (if applicable), so we can convert to rgb for display.

        voxels (bool): if True, and we have a 3d conv, show the voxels
        alpha (float): only applicable if voxels=True
        stride (list): only applicable if voxels=True

    Returns:
        matplotlib.figure.Figure: fig - a Matplotlib figure

    References:
        https://matplotlib.org/devdocs/gallery/mplot3d/voxels.html

    Example:
        >>> # xdoctest: +REQUIRES(module:torch)
        >>> conv = torch.nn.Conv2d(3, 9, (5, 7))
        >>> plot_convolutional_features(conv, colorspace=None, fnum=None, limit=2)

    Example:
        >>> # xdoctest: +REQUIRES(--comprehensive)
        >>> # xdoctest: +REQUIRES(module:torch)
        >>> import torchvision
        >>> # 2d uncolored gray-images
        >>> conv = torch.nn.Conv3d(1, 2, (3, 4, 5))
        >>> plot_convolutional_features(conv, colorspace=None, fnum=1, limit=2)

        >>> # 2d colored rgb-images
        >>> conv = torch.nn.Conv3d(3, 2, (6, 4, 5))
        >>> plot_convolutional_features(conv, colorspace='rgb', fnum=1, limit=2)

        >>> # 2d uncolored rgb-images
        >>> conv = torch.nn.Conv3d(3, 2, (6, 4, 5))
        >>> plot_convolutional_features(conv, colorspace=None, fnum=1, limit=2)

        >>> # 3d gray voxels
        >>> conv = torch.nn.Conv3d(1, 2, (6, 4, 5))
        >>> plot_convolutional_features(conv, colorspace=None, fnum=1, voxels=True,
        >>>                             limit=2)

        >>> # 3d color voxels
        >>> conv = torch.nn.Conv3d(3, 2, (6, 4, 5))
        >>> plot_convolutional_features(conv, colorspace='rgb', fnum=1,
        >>>                             voxels=True, alpha=1, limit=3)

        >>> # hack the nice resnet weights into 3d-space
        >>> # xdoctest: +REQUIRES(--network)
        >>> import torchvision
        >>> model = torchvision.models.resnet50(pretrained=True)
        >>> conv = torch.nn.Conv3d(3, 1, (7, 7, 7))
        >>> weights_tohack = model.conv1.weight[0:7].data.numpy()
        >>> # normalize each weight for nice colors, then place in the conv3d
        >>> for w in weights_tohack:
        ...     w[:] = (w - w.min()) / (w.max() - w.min())
        >>> weights_hacked = weights_tohack.transpose(1, 0, 2, 3)[None, :]
        >>> conv.weight.data[:] = torch.FloatTensor(weights_hacked)

        >>> plot_convolutional_features(conv, colorspace='rgb', fnum=1, voxels=True, alpha=.6)

        >>> plot_convolutional_features(conv, colorspace='rgb', fnum=2, voxels=False, alpha=.9)

    Example:
        >>> # xdoctest: +REQUIRES(--network)
        >>> # xdoctest: +REQUIRES(module:torch)
        >>> import torchvision
        >>> model = torchvision.models.resnet50(pretrained=True)
        >>> conv = model.conv1
        >>> plot_convolutional_features(conv, colorspace='rgb', fnum=None)

    """
    import kwplot
    kwplot.autompl()
    import matplotlib.pyplot as plt

    # get relavent data out of pytorch module
    weights = conv.weight.data.cpu().numpy()
    in_channels = conv.in_channels
    # out_channels = conv.out_channels
    kernel_size = conv.kernel_size
    conv_dim = len(kernel_size)

    # TODO: use make_conv_images in the 2d case here

    if voxels:
        # use up to 3 spatial dimensions
        spatial_axes = list(kernel_size[-3:])
    else:
        # use only 2 spatial dimensions
        spatial_axes = list(kernel_size[-2:])
    color_axes = []

    output_axis = 0

    # If there are 3 input channels, we can visualize features in a colorspace
    if colorspace is not None and in_channels == 3:
        # Move colorable channels to the end (handle 1, 2 and 3d convolution)
        axes = [0] + list(range(2, 2 + conv_dim)) + [1]
        weights = weights.transpose(*axes)
        color_axes = [in_channels]
        output_axis = 0
    else:
        pass

    # Normalize layer weights between 0 and 1
    if normaxis is None:
        minval = weights.min()
        maxval = weights.max()
    else:
        # if normaxis=0 norm over output channels
        minval = weights.min(axis=output_axis, keepdims=True)
        maxval = weights.max(axis=output_axis, keepdims=True)

    weights_norm = (weights - minval) / (maxval - minval)

    if _hack_2drows:
        # To agree with jason's visualization for a paper figure
        if not voxels:
            weights_norm = weights_norm.transpose(1, 0, 2, 3)

    # flatten everything but the spatial and requested color dims
    weights_flat = weights_norm.reshape(-1, *(spatial_axes + color_axes))

    num_plots = min(weights_flat.shape[0], limit)
    dim = int(np.ceil(np.sqrt(num_plots)))

    if voxels:
        from mpl_toolkits.mplot3d import Axes3D  # NOQA
        filled = np.ones(spatial_axes, dtype=np.bool)
        # np.ones(spatial_axes)
        # d, h, w = np.indices(spatial_axes)

    fnum = kwplot.ensure_fnum(fnum)
    fig = kwplot.figure(fnum=fnum)
    fig.clf()
    if nCols is None:
        nCols = dim
    pnum_ = kwplot.PlotNums(nCols=nCols, nSubplots=num_plots)

    def plot_kernel3d(i):
        img = weights_flat[i]

        # fig = kwplot.figure(fnum=fnum, pnum=pnum_[i])
        ax = fig.add_subplot(*pnum_[i], projection='3d')
        # ax = fig.gca(projection='3d')

        alpha_ = (filled * alpha)[..., None]
        colors = img

        if not color_axes:
            import kwimage
            # transform grays into colors
            grays = kwimage.atleast_nd(img, 4)
            colors = np.concatenate([grays, grays, grays], axis=3)

        if colorspace and color_axes:
            import kwimage
            # convert into RGB
            for d in range(len(colors)):
                colors[d] = kwimage.convert_colorspace(colors[d],
                                                       src_space=colorspace,
                                                       dst_space='rgb')
        facecolors = np.concatenate([colors, alpha_], axis=3)

        # shuffle dims so height is upwards and depth move away from us.
        dim_labels = ['d', 'h', 'w']
        axes = [2, 0, 1]

        dim_labels = list(ub.take(dim_labels, axes))
        facecolors = facecolors.transpose(*(axes + [3]))
        filled_ = filled.transpose(*axes)
        spatial_axes_ = list(ub.take(spatial_axes, axes))

        # ax.voxels(filled_, facecolors=facecolors, edgecolors=facecolors)
        if False:
            ax.voxels(filled_, facecolors=facecolors, edgecolors='k')
        else:
            # hack to show "occluded" voxels
            # stride = [1, 3, 1]
            stride = [2, 2, 2]
            slices = tuple(slice(None, None, s) for s in stride)
            spatial_axes2 = list(np.array(spatial_axes_) * stride)
            filled2 = np.zeros(spatial_axes2, dtype=np.bool)
            facecolors2 = np.empty(spatial_axes2 + [4], dtype=np.float32)
            filled2[slices] = filled_
            facecolors2[slices] = facecolors
            edgecolors2 = [0, 0, 0, alpha]
            # 'k'
            # edgecolors2 = facecolors2

            # Shrink the gaps, which let you see occluded voxels
            x, y, z = np.indices(np.array(filled2.shape) + 1).astype(float) // 2
            x[0::2, :, :] += 0.05
            y[:, 0::2, :] += 0.05
            z[:, :, 0::2] += 0.05
            x[1::2, :, :] += 0.95
            y[:, 1::2, :] += 0.95
            z[:, :, 1::2] += 0.95

            ax.voxels(x, y, z, filled2, facecolors=facecolors2, edgecolors=edgecolors2)

        for xyz, dlbl in zip(['x', 'y', 'z'], dim_labels):
            getattr(ax, 'set_' + xyz + 'label')(dlbl)

        for xyz in ['x', 'y', 'z']:
            getattr(ax, 'set_' + xyz + 'ticks')([])

        ax.set_aspect('equal')
        if not labels or i < num_plots - 1:
            # show axis only on the last plot
            ax.grid(False)
            plt.axis('off')

    for i in ub.ProgIter(range(num_plots), desc='plot conv layer',
                         enabled=False):
        if voxels:
            plot_kernel3d(i)
        else:
            img = weights_flat[i]
            kwplot.imshow(img, fnum=fnum, pnum=pnum_[i],
                          interpolation='nearest', colorspace=colorspace)
    return fig
