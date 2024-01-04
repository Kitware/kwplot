The Kitware Plot Module
=======================

|GitlabCIPipeline| |GitlabCICoverage| |Appveyor| |Pypi| |Downloads| |ReadTheDocs|

+------------------+------------------------------------------------------+
| ReadTheDocs      | https://kwplot.readthedocs.io/en/latest/             |
+------------------+------------------------------------------------------+
| Gitlab (main)    | https://gitlab.kitware.com/computer-vision/kwplot    |
+------------------+------------------------------------------------------+
| Github (mirror)  | https://github.com/Kitware/kwplot                    |
+------------------+------------------------------------------------------+
| Pypi             | https://pypi.org/project/kwplot                      |
+------------------+------------------------------------------------------+

The ``kwplot`` module is a wrapper around ``matplotlib`` and can be used for
visualizing algorithm results.

The top-level API is:

.. code:: python

    from .auto_backends import (autompl, autoplt, set_mpl_backend,)
    from .draw_conv import (make_conv_images, plot_convolutional_features,)
    from .mpl_3d import (plot_surface3d,)
    from .mpl_color import (Color,)
    from .mpl_core import (distinct_colors, distinct_markers, ensure_fnum, figure,
                           imshow, legend, next_fnum, set_figtitle,
                           show_if_requested,)
    from .mpl_draw import (draw_boxes, draw_boxes_on_image, draw_clf_on_image,
                           draw_line_segments, draw_text_on_image, plot_matrix, draw_points,)
    from .mpl_make import (make_heatmask, make_orimask, make_vector_field,)
    from .mpl_multiplot import (multi_plot,)
    from .mpl_plotnums import (PlotNums,)

One of the key features is the `kwplot.autompl <https://kwplot.readthedocs.io/en/main/kwplot.html#kwplot.autompl>`_
function, which is able to somewhat intelligently set the notorious matplotlib
backend.
By default it will attempt to use ``PyQt5`` if it is installed and a
``DISPLAY`` is available. Otherwise it will ensure the backend is set to
``Agg``. For convinience, the functions:
`kwplot.autoplt <https://kwplot.readthedocs.io/en/main/kwplot.html#kwplot.autoplt>`_ and
`kwplot.autosns <https://kwplot.readthedocs.io/en/main/kwplot.html#kwplot.autosns>`_
also execute this auto-backend behavior, but return the pyplot and seaborn
module, respectively.  It is recommended to call one of these functions before
any use of pyplot due to pyplot's import-time side effects (note: pre-importing
most other matplotlib modules is ok).

The ``kwplot.imshow`` and ``kwplot.figure`` functions are extensions of the
``matplotlib`` versions with slightly extended interfaces (again to help reduce
the density of visualization code in research scripts). The ``kwplot.PlotNums``
helps manage subplots locations, especially when you are developing /
reordering them.


.. |Pypi| image:: https://img.shields.io/pypi/v/kwplot.svg
   :target: https://pypi.python.org/pypi/kwplot

.. |Downloads| image:: https://img.shields.io/pypi/dm/kwplot.svg
   :target: https://pypistats.org/packages/kwplot

.. |ReadTheDocs| image:: https://readthedocs.org/projects/kwplot/badge/?version=main
    :target: http://kwplot.readthedocs.io/en/main/

.. # See: https://ci.appveyor.com/project/jon.crall/kwplot/settings/badges
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/py3s2d6tyfjc8lm3/branch/main?svg=true
   :target: https://ci.appveyor.com/project/jon.crall/kwplot/branch/main

.. |GitlabCIPipeline| image:: https://gitlab.kitware.com/computer-vision/kwplot/badges/main/pipeline.svg
   :target: https://gitlab.kitware.com/computer-vision/kwplot/-/jobs

.. |GitlabCICoverage| image:: https://gitlab.kitware.com/computer-vision/kwplot/badges/main/coverage.svg
    :target: https://gitlab.kitware.com/computer-vision/kwplot/commits/main
