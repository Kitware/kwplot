# The Kitware Plot Module

The `kwplot` module is a wrapper around `matplotlib` and can be used for
visualizing algorithm results.

One of the key features is the `kwplot.autompl` function, which is able to somewhat
intelligently set the notorious matplotlib backend. By default it will attempt
to use `PyQt5` if it is installed and a `DISPLAY` is available. Otherwise it
will ensure the backend is set to `Agg`.

The `kwplot.multi_plot` function is able to create line and bar plots with
multiple lines/bars in a labeled axes using only a single function call. This
can dramatically reduce the code size needed to perform simple plot
visualizations as well as ensure that the code that produces the data is
decoupled from the code that does the visualization.

The `kwplot.imshow` and `kwplot.figure` functions are extensions of the
`matplotlib` versions with slightly extended interfaces (again to help reduce
the density of visualization code in research scripts).
