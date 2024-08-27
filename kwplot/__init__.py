"""
KWPlot - The Kitware Plot Module
================================

+------------------+------------------------------------------------------+
| ReadTheDocs      | https://kwplot.readthedocs.io/en/latest/             |
+------------------+------------------------------------------------------+
| Gitlab (main)    | https://gitlab.kitware.com/computer-vision/kwplot    |
+------------------+------------------------------------------------------+
| Github (mirror)  | https://github.com/Kitware/kwplot                    |
+------------------+------------------------------------------------------+
| Pypi             | https://pypi.org/project/kwplot                      |
+------------------+------------------------------------------------------+

This module is a small wrapper around matplotlib and seaborn that simplifies
developer workflow when working with code that might be run in IPython or in a
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
feature of any library, so we still recommend putting that code inside the
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

__version__ = '0.5.1'
__author__ = 'Kitware Inc., Jon Crall'
__author_email__ = 'kitware@kitware.com, jon.crall@kitware.com'
__url__ = 'https://gitlab.kitware.com/computer-vision/kwplot'

__mkinit__ = """
mkinit kwplot -w --relative --nomods --lazy
mkinit kwplot --diff --relative --nomods --lazy
"""

__private__ = ['video_writer']


class __module_properties__:
    """
    experimental mkinit feature for handling module level properties.

    References:
        https://github.com/scientific-python/lazy-loader/issues/127
    """

    @property
    def plt(self):
        import kwplot
        return kwplot.autoplt()

    @property
    def sns(self):
        import kwplot
        return kwplot.autosns()

    @property
    def pyplot(self):
        import kwplot
        return kwplot.autoplt()

    @property
    def seaborn(self):
        import kwplot
        return kwplot.autosns()

    @property
    def Color(self):
        # Backwards compat
        from kwimage import Color
        return Color

# TODO: figure out better way to handle module properties
# POC_MODULE_PROEPRTY = 2
# if POC_MODULE_PROEPRTY == 1:
#     # Python 3.7+ only, experimental auto function support via properties
#     # See Also: https://stackoverflow.com/questions/880530/can-modules-have-properties-the-same-way-that-objects-can

#     __module_properties__ = {}

#     def module_property(func):
#         __module_properties__[func.__name__] = property(func)

#     @module_property
#     def plt():
#         import kwplot
#         return kwplot.autoplt()
#     del plt

#     @module_property
#     def sns():
#         import kwplot
#         return kwplot.autosns()
#     del sns

#     def __getattr__(key):
#         print(f'getattr key={key}')
#         if key in __module_properties__:
#             prop = __module_properties__[key]
#             return prop.fget()
#         raise AttributeError(key)
#     __all__ += ['sns', 'plt']
# elif POC_MODULE_PROEPRTY == 2:
#     # This seems to be a more stable way of handling module properties
#     __all__ += ['plt', 'sns']
#     def __getattr__(key):
#         # Make these special auto-backends top-level dynamic properties of kwplot
#         if key == 'plt':
#             import kwplot
#             return kwplot.autoplt()
#         if key == 'sns':
#             import kwplot
#             return kwplot.autosns()
#         raise AttributeError(key)


def lazy_import(module_name, submodules, submod_attrs, eager='auto'):
    import importlib
    import os
    name_to_submod = {
        func: mod for mod, funcs in submod_attrs.items()
        for func in funcs
    }
    module_property_names = {'Color', 'plt', 'sns', 'seaborn', 'pyplot'}
    modprops = __module_properties__()
    def __getattr__(name):
        if name in module_property_names:
            return getattr(modprops, name)
        if name in submodules:
            attr = importlib.import_module(
                '{module_name}.{name}'.format(
                    module_name=module_name, name=name)
            )
        elif name in name_to_submod:
            submodname = name_to_submod[name]
            module = importlib.import_module(
                '{module_name}.{submodname}'.format(
                    module_name=module_name, submodname=submodname)
            )
            attr = getattr(module, name)
        else:
            raise AttributeError(
                f'Module {module_name!r} has no attribute {name!r}')
        globals()[name] = attr
        return attr
    eager_import_flag = False
    if eager == 'auto':
        eager_import_text = os.environ.get('EAGER_IMPORT', '')
        if eager_import_text:
            eager_import_text_ = eager_import_text.lower()
            if eager_import_text_ in {'true', '1', 'on', 'yes'}:
                eager_import_flag = True

        eager_import_module_text = os.environ.get('EAGER_IMPORT_MODULES', '')
        if eager_import_module_text:
            if eager_import_module_text.lower() in __name__.lower():
                eager_import_flag = True
    else:
        eager_import_flag = eager
    if eager_import_flag:
        for name in submodules:
            __getattr__(name)

        for attrs in submod_attrs.values():
            for attr in attrs:
                __getattr__(attr)
    return __getattr__

__getattr__ = lazy_import(
    __name__,
    submodules={},
    submod_attrs={
        'auto_backends': [
            'BackendContext',
            'autompl',
            'autoplt',
            'autosns',
            'set_mpl_backend',
        ],
        'draw_conv': [
            'make_conv_images',
            'plot_convolutional_features',
        ],
        'managers': [
            'ArtistManager',
            'FigureFinalizer',
            'FigureManager',
            'LabelManager',
            'Palette',
            'PaletteManager',
            'cropwhite_ondisk',
            'extract_legend',
            'fix_matplotlib_dates',
            'fix_matplotlib_timedeltas',
        ],
        'mpl_3d': [
            'plot_points3d',
            'plot_surface3d',
        ],
        'mpl_color': [
            'Color',
        ],
        'mpl_core': [
            'FigureAxes',
            'all_figures',
            'close_figures',
            'distinct_colors',
            'distinct_markers',
            'ensure_fnum',
            'figure',
            'imshow',
            'legend',
            'next_fnum',
            'phantom_legend',
            'set_figtitle',
            'show_if_requested',
        ],
        'mpl_draw': [
            'draw_boxes',
            'draw_boxes_on_image',
            'draw_clf_on_image',
            'draw_line_segments',
            'draw_points',
            'draw_text_on_image',
            'plot_matrix',
        ],
        'mpl_make': [
            'make_heatmask',
            'make_legend_img',
            'make_orimask',
            'make_vector_field',
            'render_figure_to_image',
        ],
        'mpl_multiplot': [
            'multi_plot',
        ],
        'mpl_plotnums': [
            'PlotNums',
        ],
        'tables': [
            'dataframe_table',
            'humanize_dataframe',
        ],
    },
)


def __dir__():
    return __all__

__all__ = ['ArtistManager', 'BackendContext', 'Color', 'FigureAxes',
           'FigureFinalizer', 'FigureManager', 'LabelManager', 'Palette',
           'PaletteManager', 'PlotNums', 'all_figures', 'autompl', 'autoplt',
           'autosns', 'close_figures', 'cropwhite_ondisk', 'dataframe_table',
           'distinct_colors', 'distinct_markers', 'draw_boxes',
           'draw_boxes_on_image', 'draw_clf_on_image', 'draw_line_segments',
           'draw_points', 'draw_text_on_image', 'ensure_fnum',
           'extract_legend', 'figure', 'fix_matplotlib_dates',
           'fix_matplotlib_timedeltas', 'humanize_dataframe', 'imshow',
           'legend', 'make_conv_images', 'make_heatmask', 'make_legend_img',
           'make_orimask', 'make_vector_field', 'multi_plot', 'next_fnum',
           'phantom_legend', 'plot_convolutional_features', 'plot_matrix',
           'plot_points3d', 'plot_surface3d', 'plt', 'render_figure_to_image',
           'set_figtitle', 'set_mpl_backend', 'show_if_requested', 'sns',
           'pyplot', 'seaborn']
