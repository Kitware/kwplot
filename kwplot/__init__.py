"""
mkinit ~/code/kwplot/kwplot/__init__.py -w --relative --nomods
"""

__version__ = '0.3.0'

from .auto_backends import (autompl, autoplt, set_mpl_backend,)
from .draw_conv import (make_conv_images, plot_convolutional_features,)
from .mpl_3d import (plot_surface3d,)
from .mpl_color import (Color,)
from .mpl_core import (distinct_colors, distinct_markers, ensure_fnum, figure,
                       imshow, legend, next_fnum, set_figtitle,
                       show_if_requested,)
from .mpl_draw import (draw_boxes, draw_clf_on_image, draw_line_segments,
                       plot_matrix,)
from .mpl_make import (make_heatmask, make_orimask, make_vector_field,)
from .mpl_multiplot import (multi_plot,)
from .mpl_plotnums import (PlotNums,)

__all__ = ['Color', 'PlotNums', 'autompl', 'autoplt', 'distinct_colors',
           'distinct_markers', 'draw_boxes', 'draw_clf_on_image',
           'draw_line_segments', 'ensure_fnum', 'figure', 'imshow', 'legend',
           'make_conv_images', 'make_heatmask', 'make_orimask',
           'make_vector_field', 'multi_plot', 'next_fnum',
           'plot_convolutional_features', 'plot_matrix', 'plot_surface3d',
           'set_figtitle', 'set_mpl_backend', 'show_if_requested']
