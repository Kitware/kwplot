"""
Helpers for seaborn
"""


class MonkeyPatchPyPlotFigureContext:
    """
    😢 🙈 😭

    Forces all calls of plt.figure to return a specific figure in this context.

    References:
        ..[Seaborn2830] https://github.com/mwaskom/seaborn/issues/2830

    CommandLine:
        TEST_MONKEY=1 xdoctest -m kwcoco.cli.coco_plot_stats MonkeyPatchPyPlotFigureContext

    Example:
        >>> # xdoctest: +REQUIRES(env:TEST_MONKEY)
        >>> from kwplot.util_seaborn import *  # NOQA
        >>> import matplotlib.pyplot as plt
        >>> func1 = plt.figure
        >>> self = MonkeyPatchPyPlotFigureContext('mockfig')
        >>> with self:
        >>>     func2 = plt.figure
        >>> func3 = plt.figure
        >>> print(f'func1={func1}')
        >>> print(f'func2={func2}')
        >>> print(f'func3={func3}')
        >>> assert func1 is func3
        >>> assert func1 is not func2
    """
    def __init__(self, fig):
        from matplotlib import pyplot as plt
        self.fig = fig
        self.plt = plt
        self._monkey_attrname = '__monkey_for_seaborn_issue_2830__'
        self._orig_figure = None

    def figure(self, *args, **kwargs):
        """
        Our hacked version of the figure function
        """
        return self.fig

    def _getmonkey(self):
        """
        Check if there is a monkey attached to pyplot
        """
        return getattr(self.plt, self._monkey_attrname, None)

    def _setmonkey(self):
        """
        We are the monkey now
        """
        assert self._getmonkey() is None
        assert self._orig_figure is None
        # TODO: make thread safe?
        setattr(self.plt, self._monkey_attrname, 'setting-monkey')
        self._orig_figure = self.plt.figure
        self.plt.figure = self.figure
        setattr(self.plt, self._monkey_attrname, self)

    def _delmonkey(self):
        """
        Get outta here monkey
        """
        assert self._getmonkey() is self
        assert self._orig_figure is not None
        setattr(self.plt, self._monkey_attrname, 'removing-monkey')
        self.plt.figure = self._orig_figure
        setattr(self.plt, self._monkey_attrname, None)

    def __enter__(self):
        current_monkey = self._getmonkey()
        if current_monkey is None:
            self._setmonkey()
        else:
            raise NotImplementedError('no reentrancy for now')

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self._delmonkey()
        if ex_traceback is not None:
            return False


def histplot_splity(data, x, split_y='auto', **snskw):
    """
    Like :func:`seaborn.histplot`, but can split the y axis across two parts.

    Useful for data where you want a linear scale for larger frequencies, but
    also you want to see the smaller frequencies.

    Args:
        data (DataFrame): data to plot

        x (str): column of the data to plot over the x axis

        split_y (str | Number):
            the local to split the y axis into two plots.
            Defaults to "auto" and attempts to figure it out.
            if None, falls back to regular histplot.

        **snskw: passed to :func:`seaborn.histplot`.

    References:
        https://stackoverflow.com/questions/32185411/break-in-x-axis-of-matplotlib
        https://stackoverflow.com/questions/63726234/how-to-draw-a-broken-y-axis-catplot-graphes-with-seaborn

    Example:
        >>> # xdoctest: +REQUIRES(module:seaborn)
        >>> # xdoctest: +REQUIRES(module:pandas)
        >>> from kwplot.util_seaborn import *  # NOQA
        >>> import kwplot
        >>> import pandas as pd
        >>> import numpy as np
        >>> import kwarray
        >>> rng = kwarray.ensure_rng(0)
        >>> num_rows = 1000
        >>> columns = {
        >>>     'nums1': rng.rand(num_rows) * 10,
        >>>     'nums2': rng.rand(num_rows),
        >>>     'cats1': rng.randint(0, 3, num_rows),
        >>>     'cats2': rng.randint(0, 3, num_rows),
        >>>     'cats3': np.random.randint(0, 3, num_rows),
        >>>     'const1': ['a'] * num_rows,
        >>>     'strs1': [rng.choice(list('abc')) for _ in range(num_rows)],
        >>> }
        >>> data = pd.DataFrame(columns)
        >>> data['nums1'].iloc[0:700] = 12  # force a split point to be reasonable
        >>> histplot_splity(data=data, x='nums1')
        >>> kwplot.show_if_requested()
    """
    import kwplot
    sns = kwplot.sns
    plt = kwplot.plt
    ax = snskw.get('ax', None)

    if split_y == 'auto':
        if ax is not None:
            raise Exception(f'The ax argument cannot be specified unless split_y is None, got split_y={split_y}')
        histogram = data[x].value_counts()
        small_values = histogram[histogram < histogram.mean()]
        try:
            split_y = int(small_values.max() * 1.5)
            if split_y < 20:
                split_y = 20
        except ValueError:
            split_y = None

    if snskw is None:
        snskw = dict(binwidth=1, discrete=True)
        snskw = dict()

    if split_y is None:
        if ax is None:
            ax = kwplot.figure(fnum=1, doclf=True).gca()
        ax_top = ax_bottom = ax
        sns.histplot(data=data, x=x, ax=ax_top, **snskw)
        return ax_top, ax_bottom, split_y

    if ax is not None:
        raise Exception('The ax argument cannot be specified if using a split plot')

    # Q: is it possible to pass this an existing figure, so we don't always
    # create a new one with plt.subplots?
    # A: No, but we can specify keyword args
    fig_kw = {'num': 1, 'clear': True}
    fig, (ax_top, ax_bottom) = plt.subplots(
        ncols=1, nrows=2, sharex=True,
        gridspec_kw={'hspace': 0.05},
        **fig_kw
    )

    sns.histplot(data=data, x=x, ax=ax_top, **snskw)
    sns.histplot(data=data, x=x, ax=ax_bottom, **snskw)

    sns.despine(ax=ax_bottom)
    sns.despine(ax=ax_top, bottom=True)
    ax = ax_top
    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal

    ax2 = ax_bottom
    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal

    #remove one of the legend
    if ax_bottom.legend_ is not None:
        ax_bottom.legend_.remove()

    ax_top.set_ylabel('')
    ax_top.set_ylim(bottom=split_y)   # those limits are fake
    ax_bottom.set_ylim(0, split_y)
    return ax_top, ax_bottom, split_y
