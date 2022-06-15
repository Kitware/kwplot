"""
KWPlot - The Kitware Plot Module
================================

This module is a small wrapper around matplotlib and seaborn that simplifies
develoepr workflow when working with code that might be run in IPython or in a
script. This is primarilly handled by the :mod:`kwplot.auto_backends` module,
which exposes the functions: :func:`kwplot.autompl`, :func:`kwplot.autoplt`,
and :func:`kwplot.autosns` for auto-initialization of matplotlib, pyplot, and
seaborn.

A very common anti-pattern in developer code is importing
:mod:`matplotlib.pyplot` at the top level of your module. This is a mistake
because importing pyplot has side-effects which can cause problems if
executed at a module level (i.e. they happen at import time! Anyone using
your library will have to deal with these consequences )


To mitigate this we recommend only using pyplot inside of the scope of the
functions that need it.

Importing :mod:`kwplot` itself has no import-time side effects, so it is safe
to put it as a module level import, however, plotting is often an optional
feature of any library, so we still recomend putting that code inside the
functions that need it.

The general code flow looks like this, inside your function run:

.. code:: python

    import kwplot
    kwplot.autompl()

    # Pyplot is now initialized do matplotlib or pyplot stuff
    ...


This checks if you are running interactively in IPython, if so try to use a Qt
backend. If not, then try to use a headless Agg backend.


You can also do

.. code:: python

    import kwplot
    # These also call autompl in the backend, and return either the seaborn or
    # pyplot modules, so you dont have to import them in your code. When
    # running seaborn, this will also call ``sns.set()`` for you.
    sns = kwplot.autosns()
    plt = kwplot.autoplt()
    ...


In addition to this auto-backend feature, kwplot also exposes useful helper
methods for common drawing operations.

There is also a small CLI that can be used to view multispectral or uint16
images.
"""

__version__ = '0.4.12'
__author__ = 'Kitware Inc., Jon Crall'
__author_email__ = 'kitware@kitware.com, jon.crall@kitware.com'
__url__ = 'https://gitlab.kitware.com/computer-vision/kwplot'

__mkinit__ = """
mkinit -m kwplot -w --relative --nomods
mkinit -m kwplot --diff --relative --nomods
"""

# Backwards compat
from kwimage import Color  # noqa

from .auto_backends import (BackendContext, autompl, autoplt, autosns,
                            set_mpl_backend,)
from .draw_conv import (make_conv_images, plot_convolutional_features,)
from .mpl_3d import (plot_surface3d,)
from .mpl_core import (all_figures, close_figures, distinct_colors,
                       distinct_markers, ensure_fnum, figure, imshow, legend,
                       next_fnum, phantom_legend, set_figtitle,
                       show_if_requested,)
from .mpl_draw import (draw_boxes, draw_boxes_on_image, draw_clf_on_image,
                       draw_line_segments, draw_points, draw_text_on_image,
                       plot_matrix,)
from .mpl_make import (make_heatmask, make_legend_img, make_orimask,
                       make_vector_field, render_figure_to_image,)
from .mpl_multiplot import (multi_plot,)
from .mpl_plotnums import (PlotNums,)


__all__ = ['BackendContext', 'Color', 'PlotNums', 'all_figures', 'autompl',
           'autoplt', 'autosns', 'close_figures', 'distinct_colors',
           'distinct_markers', 'draw_boxes', 'draw_boxes_on_image',
           'draw_clf_on_image', 'draw_line_segments', 'draw_points',
           'draw_text_on_image', 'ensure_fnum', 'figure', 'imshow', 'legend',
           'make_conv_images', 'make_heatmask', 'make_legend_img',
           'make_orimask', 'make_vector_field', 'multi_plot', 'next_fnum',
           'phantom_legend', 'plot_convolutional_features', 'plot_matrix',
           'plot_surface3d', 'render_figure_to_image', 'set_figtitle',
           'set_mpl_backend', 'show_if_requested']
