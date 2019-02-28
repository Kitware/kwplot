"""
mkinit ~/code/kwplot/kwplot/__init__.py -w --relative
"""

__version__ = '0.3.0.dev0'

from . import auto_backends
from . import draw_conv
from . import mpl_color
from . import mpl_core
from . import mpl_draw
from . import mpl_make
from . import mpl_multiplot
from . import mpl_plotnums

from .auto_backends import (autompl, set_mpl_backend,)
from .draw_conv import (make_conv_images, plot_convolutional_features,)
from .mpl_color import (Color,)
from .mpl_core import (distinct_colors, distinct_markers, ensure_fnum, figure,
                       imshow, legend, next_fnum, set_figtitle,
                       show_if_requested,)
from .mpl_draw import (draw_boxes, draw_clf_on_image, draw_line_segments,
                       plot_matrix,)
from .mpl_make import (make_heatmask, make_orimask, make_vector_field,)
from .mpl_multiplot import (multi_plot,)
from .mpl_plotnums import (PlotNums,)

__all__ = ['Color', 'PlotNums', 'auto_backends', 'autompl', 'distinct_colors',
           'distinct_markers', 'draw_boxes', 'draw_clf_on_image', 'draw_conv',
           'draw_line_segments', 'ensure_fnum', 'figure', 'imshow', 'legend',
           'make_conv_images', 'make_heatmask', 'make_orimask',
           'make_vector_field', 'mpl_color', 'mpl_core', 'mpl_draw',
           'mpl_make', 'mpl_multiplot', 'mpl_plotnums', 'multi_plot',
           'next_fnum', 'plot_convolutional_features', 'plot_matrix',
           'set_figtitle', 'set_mpl_backend', 'show_if_requested']
