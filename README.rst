The Kitware Plot Module
=======================

|GitlabCIPipeline| |GitlabCICoverage| |Appveyor| |Pypi| |Downloads| 

The main webpage for this project is: https://gitlab.kitware.com/computer-vision/kwplot

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

One of the key features is the ``kwplot.autompl`` function, which is able to somewhat
intelligently set the notorious matplotlib backend. By default it will attempt
to use ``PyQt5`` if it is installed and a ``DISPLAY`` is available. Otherwise it
will ensure the backend is set to ``Agg``.

The ``kwplot.multi_plot`` function is able to create line and bar plots with
multiple lines/bars in a labeled axes using only a single function call. This
can dramatically reduce the code size needed to perform simple plot
visualizations as well as ensure that the code that produces the data is
decoupled from the code that does the visualization.

The ``kwplot.imshow`` and ``kwplot.figure`` functions are extensions of the
``matplotlib`` versions with slightly extended interfaces (again to help reduce
the density of visualization code in research scripts).


.. |Pypi| image:: https://img.shields.io/pypi/v/kwplot.svg
   :target: https://pypi.python.org/pypi/kwplot

.. |Downloads| image:: https://img.shields.io/pypi/dm/kwplot.svg
   :target: https://pypistats.org/packages/kwplot

.. |ReadTheDocs| image:: https://readthedocs.org/projects/kwplot/badge/?version=latest
    :target: http://kwplot.readthedocs.io/en/latest/

.. # See: https://ci.appveyor.com/project/jon.crall/kwplot/settings/badges
.. |Appveyor| image:: https://ci.appveyor.com/api/projects/status/py3s2d6tyfjc8lm3/branch/master?svg=true
   :target: https://ci.appveyor.com/project/jon.crall/kwplot/branch/master

.. |GitlabCIPipeline| image:: https://gitlab.kitware.com/computer-vision/kwplot/badges/master/pipeline.svg
   :target: https://gitlab.kitware.com/computer-vision/kwplot/-/jobs

.. |GitlabCICoverage| image:: https://gitlab.kitware.com/computer-vision/kwplot/badges/master/coverage.svg?job=coverage
    :target: https://gitlab.kitware.com/computer-vision/kwplot/commits/master
