"""
Helper for making 3D plots
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from mpl_toolkits.mplot3d.axes3d import Axes3D


def plot_surface3d(
        xgrid: Any, ygrid: Any, zdata: Any,
        xlabel: Optional[str] = None, ylabel: Optional[str] = None,
        zlabel: Optional[str] = None, wire: bool = False,
        mode: Optional[str] = None, contour: bool = False,
        rstride: int = 1, cstride: int = 1,
        pnum: Optional[Tuple[int, int, int]] = None,
        labelkw: Optional[Dict[str, Any]] = None,
        xlabelkw: Optional[Dict[str, Any]] = None,
        ylabelkw: Optional[Dict[str, Any]] = None,
        zlabelkw: Optional[Dict[str, Any]] = None,
        titlekw: Optional[Dict[str, Any]] = None,
        *args: Any, **kwargs: Any,
) -> Axes3D:
    r"""
    References:
        https://matplotlib.org/2.0.2/mpl_toolkits/mplot3d/tutorial.html

    Example:
        >>> # xdoctest: +SKIP
        >>> import kwplot
        >>> import matplotlib as mpl
        >>> import kwimage
        >>> shape=(19, 19)
        >>> sigma1, sigma2 = 2.0, 1.0
        >>> ybasis = np.arange(shape[0])
        >>> xbasis = np.arange(shape[1])
        >>> xgrid, ygrid = np.meshgrid(xbasis, ybasis)
        >>> sigma = [sigma1, sigma2]
        >>> gausspatch = kwimage.gaussian_patch(shape, sigma=sigma)
        >>> title = 'ksize={!r}, sigma={!r}'.format(shape, (sigma1, sigma2))
        >>> kwplot.plot_surface3d(xgrid, ygrid, gausspatch, rstride=1, cstride=1,
        >>>                   cmap=mpl.cm.coolwarm, title=title)
        >>> kwplot.show_if_requested()
    """
    if titlekw is None:
        titlekw = {}
    if labelkw is None:
        labelkw = {}
    if xlabelkw is None:
        xlabelkw = labelkw.copy()
    if ylabelkw is None:
        ylabelkw = labelkw.copy()
    if zlabelkw is None:
        zlabelkw = labelkw.copy()
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    cmap = kwargs.get('cmap', 'magma')
    if isinstance(cmap, str):
        kwargs['cmap'] = cmap = plt.get_cmap(cmap)
    fig = plt.gcf()
    if pnum is None:
        current_ax = plt.gca()
        if isinstance(current_ax, Axes3D):
            raw_ax = current_ax
        else:
            raw_ax = fig.add_subplot(1, 1, 1, projection='3d')
    else:
        raw_ax = fig.add_subplot(*pnum, projection='3d')
    ax = raw_ax
    title = kwargs.pop('title', None)
    if mode is None:
        mode = 'wire' if wire else 'surface'

    if len(xgrid.shape) == 1:
        # TODO: if we are given long-form data points can we quickly check and
        # reshape to the necessary grid
        pass
        # maybe use ax.scatter3D

    if mode == 'wire':
        ax.plot_wireframe(xgrid, ygrid, zdata, rstride=rstride,
                          cstride=cstride, *args, **kwargs)
        #ax.contour(xgrid, ygrid, zdata, rstride=rstride, cstride=cstride,
        #extend3d=True, *args, **kwargs)
    elif mode == 'surface' :
        ax.plot_surface(xgrid, ygrid, zdata, rstride=rstride, cstride=cstride,
                        linewidth=.1, *args, **kwargs)
    else:
        raise NotImplementedError('mode=%r' % (mode,))
    if contour:
        xoffset = xgrid.min() - ((xgrid.max() - xgrid.min()) * .1)
        yoffset = ygrid.max() + ((ygrid.max() - ygrid.min()) * .1)
        zoffset = zdata.min() - ((zdata.max() - zdata.min()) * .1)
        cmap = kwargs.get('cmap', plt.get_cmap('coolwarm'))
        ax.contour(xgrid, ygrid, zdata, zdir='x', offset=xoffset, cmap=cmap)
        ax.contour(xgrid, ygrid, zdata, zdir='y', offset=yoffset, cmap=cmap)
        ax.contour(xgrid, ygrid, zdata, zdir='z', offset=zoffset, cmap=cmap)
        #ax.plot_trisurf(xgrid.flatten(), ygrid.flatten(), zdata.flatten(), *args, **kwargs)
    if title is not None:
        ax.set_title(title, **titlekw)
    if xlabel is not None:
        ax.set_xlabel(xlabel, **xlabelkw)
    if ylabel is not None:
        ax.set_ylabel(ylabel, **ylabelkw)
    if zlabel is not None:
        ax.set_zlabel(zlabel, **zlabelkw)
    return ax


def plot_points3d(
        xgrid: Any, ygrid: Any, zdata: Any,
        xlabel: Optional[str] = None, ylabel: Optional[str] = None,
        zlabel: Optional[str] = None, mode: Optional[str] = None,
        pnum: Optional[Tuple[int, int, int]] = None,
        labelkw: Optional[Dict[str, Any]] = None,
        xlabelkw: Optional[Dict[str, Any]] = None,
        ylabelkw: Optional[Dict[str, Any]] = None,
        zlabelkw: Optional[Dict[str, Any]] = None,
        titlekw: Optional[Dict[str, Any]] = None,
        *args: Any, **kwargs: Any,
) -> Axes3D:
    r"""
    References:
        http://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html

    Example:
        >>> # DISABLE_DOCTEST
        >>> import kwplot
        >>> import matplotlib as mpl
        >>> import kwimage
        >>> shape=(19, 19)
        >>> sigma1, sigma2 = 2.0, 1.0
        >>> ybasis = np.arange(shape[0])
        >>> xbasis = np.arange(shape[1])
        >>> xgrid, ygrid = np.meshgrid(xbasis, ybasis)
        >>> sigma = [sigma1, sigma2]
        >>> gausspatch = kwimage.gaussian_patch(shape, sigma=sigma)
        >>> title = 'ksize={!r}, sigma={!r}'.format(shape, (sigma1, sigma2))
        >>> plot_points3d(xgrid.ravel(), ygrid.ravel(), gausspatch.ravel(),
        >>>                      cmap=mpl.cm.coolwarm, title=title)
        >>> kwplot.show_if_requested()
    """
    if titlekw is None:
        titlekw = {}
    if labelkw is None:
        labelkw = {}
    if xlabelkw is None:
        xlabelkw = labelkw.copy()
    if ylabelkw is None:
        ylabelkw = labelkw.copy()
    if zlabelkw is None:
        zlabelkw = labelkw.copy()
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    cmap = kwargs.get('cmap', 'magma')
    if isinstance(cmap, str):
        kwargs['cmap'] = cmap = plt.get_cmap(cmap)
    fig = plt.gcf()
    if pnum is None:
        current_ax = plt.gca()
        if isinstance(current_ax, Axes3D):
            raw_ax = current_ax
        else:
            raw_ax = fig.add_subplot(1, 1, 1, projection='3d')
    else:
        raw_ax = fig.add_subplot(*pnum, projection='3d')
    ax = raw_ax
    title = kwargs.pop('title', None)
    if mode is None:
        mode = 'points'

    if len(xgrid.shape) == 1:
        # TODO: if we are given long-form data points can we quickly check and
        # reshape to the necessary grid
        pass
        # maybe use ax.scatter3D

    if mode == 'line':
        ax.plot(xgrid, ygrid, zdata, *args, **kwargs)
        #ax.contour(xgrid, ygrid, zdata, rstride=rstride, cstride=cstride,
        #extend3d=True, *args, **kwargs)
    elif mode == 'points':
        ax.scatter(xgrid, ygrid, zdata, linewidth=.1, *args, **kwargs)
    else:
        raise NotImplementedError('mode=%r' % (mode,))
    if title is not None:
        ax.set_title(title, **titlekw)
    if xlabel is not None:
        ax.set_xlabel(xlabel, **xlabelkw)
    if ylabel is not None:
        ax.set_ylabel(ylabel, **ylabelkw)
    if zlabel is not None:
        ax.set_zlabel(zlabel, **zlabelkw)
    return ax
