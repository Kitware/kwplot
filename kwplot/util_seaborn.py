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

    Returns:
        Tuple[Axes, Axes, int]:
            ax_top, ax_bottom, split_y

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


def simple_plot_histogram(data, x='intensity_bin', weights='value',
                          hue=None, ax=None):
    """
    This is just histplot, but with a fixed auto-weights binner and some custom
    palette stuff.

    Args:
        data (pd.DataFrame):
            with columns: intensity_bin  value
        ax (Axes | None):
            if specified, we assume only 1 plot is made

    Example:
        >>> # xdoctest: +REQUIRES(--show)
        >>> from kwplot.util_seaborn import *  # NOQA
        >>> import pandas as pd
        >>> n = 256
        >>> data = pd.DataFrame({
        >>>     'bin': np.arange(0, n),
        >>>     'count': np.random.randint(0, 256, n),
        >>>     'channel': ['red'] * n,
        >>> })
        >>> hue = None
        >>> x = 'bin'
        >>> weights = 'count'
        >>> ax = None
        >>> kwplot.autompl()
        >>> ax = simple_plot_histogram(data, x, weights, hue, ax)
    """
    import kwplot
    sns = kwplot.autosns()

    default_config = {
        'bins': 'auto',
        'stat': 'probability',
        'fill': True,
        'element': 'step',
        'multiple': 'layer',
        'kde': True,
        'cumulative': False,
    }

    config = default_config.copy()
    palette = None

    if palette is not None:
        palette = palette.copy()
        if hue is not None:
            unique_hue_values = data[hue].unique()
            for value in unique_hue_values:
                if value not in palette:
                    palette[value] = None
            palette = _fill_missing_colors(palette)

    hist_data_kw = dict(
        x=x,
        weights=weights,
        bins=config['bins'],
        stat=config['stat'],
        hue=hue,
    )
    hist_style_kw = dict(
        palette=palette,
        fill=config['fill'],
        element=config['element'],
        multiple=config['multiple'],
        kde=config['kde'],
        cumulative=config['cumulative'],
    )

    if ax is None:
        fig = kwplot.figure(fnum=1, doclf=True)
        fig.clf()
        ax = fig.gca()

    hist_data_kw_ = hist_data_kw.copy()
    if hist_data_kw_['bins'] == 'auto':
        xvar = hist_data_kw['x']
        weightvar = hist_data_kw['weights']
        hist_data_kw_['bins'] = _weighted_auto_bins(data, xvar, weightvar)

    try:
        # We have already computed the histogram, but we can get seaborn to
        # show it using a simple trick: use weight to represent the
        # frequency that should be used for every bin.

        # https://github.com/mwaskom/seaborn/issues/2709
        sns.histplot(ax=ax, data=data.reset_index(), **hist_data_kw_, **hist_style_kw)
    except Exception:
        import ubelt as ub
        print('hist_data_kw_ = {}'.format(ub.urepr(hist_data_kw_, nl=1)))
        print('hist_style_kw = {}'.format(ub.urepr(hist_style_kw, nl=1)))
        print('ERROR')
        print(data)
        raise
        pass
    # if config['valid_range'] is not None:
    #     valid_min, valid_max = map(float, config['valid_range'].split(':'))
    #     ax.set_xlim(valid_min, valid_max)
    # ax.set_title(sensor_name)
    # maxx = sensor_df.intensity_bin.max()
    # maxx = sensor_maxes[sensor_name]
    # ax.set_xlim(0, maxx)

    return fig


def _weighted_auto_bins(data, xvar, weightvar):
    """
    Generalized histogram bandwidth estimators for weighted univariate data

    References:
        https://github.com/mwaskom/seaborn/issues/2710

    TODO:
        add to util_kwarray

    Example:
        >>> import pandas as pd
        >>> import numpy as np
        >>> n = 100
        >>> to_stack = []
        >>> rng = np.random.RandomState(432)
        >>> for group_idx in range(3):
        >>>     part_data = pd.DataFrame({
        >>>         'x': np.arange(n),
        >>>         'weights': rng.randint(0, 100, size=n),
        >>>         'hue': [f'group_{group_idx}'] * n,
        >>>     })
        >>>     to_stack.append(part_data)
        >>> data = pd.concat(to_stack).reset_index()
        >>> xvar = 'x'
        >>> weightvar = 'weights'
        >>> n_equal_bins = _weighted_auto_bins(data, xvar, weightvar)
        >>> # xdoctest: +REQUIRES(--show)
        >>> import seaborn as sns
        >>> sns.histplot(data=data, bins=n_equal_bins, x='x', weights='weights', hue='hue')
    """
    import numpy as np
    sort_df = data.sort_values(xvar)
    values = sort_df[xvar]
    weights = sort_df[weightvar]
    minval = values.iloc[0]
    maxval = values.iloc[-1]

    total = weights.sum()
    ptp = maxval - minval

    # _hist_bin_sqrt = ptp / np.sqrt(total)
    _hist_bin_sturges = ptp / (np.log2(total) + 1.0)

    cumtotal = weights.cumsum().values
    quantiles = cumtotal / cumtotal[-1]
    idx2, idx1 = np.searchsorted(quantiles, [0.75, 0.25])
    # idx2, idx1 = _weighted_quantile(weights, [0.75, 0.25])
    iqr = values.iloc[idx2] - values.iloc[idx1]
    _hist_bin_fd = 2.0 * iqr * total ** (-1.0 / 3.0)

    fd_bw = _hist_bin_fd  # Freedman-Diaconis
    sturges_bw = _hist_bin_sturges

    if fd_bw:
        bw_est = min(fd_bw, sturges_bw)
    else:
        # limited variance, so we return a len dependent bw estimator
        bw_est = sturges_bw

    # from numpy.lib.histograms import _get_outer_edges, _unsigned_subtract
    first_edge, last_edge = _get_outer_edges(values, None)
    if bw_est:
        n_equal_bins = int(np.ceil(_unsigned_subtract(last_edge, first_edge) / bw_est))
    else:
        # Width can be zero for some estimators, e.g. FD when
        # the IQR of the data is zero.
        n_equal_bins = 1

    # Take the minimum of this and the number of actual bins
    n_equal_bins = min(n_equal_bins, len(values))
    return n_equal_bins


def _get_outer_edges(a, range):
    """
    Determine the outer bin edges to use, from either the data or the range
    argument

    Note: vendored from numpy.lib._histograms_impl
    """
    import numpy as np
    if range is not None:
        first_edge, last_edge = range
        if first_edge > last_edge:
            raise ValueError(
                'max must be larger than min in range parameter.')
        if not (np.isfinite(first_edge) and np.isfinite(last_edge)):
            raise ValueError(
                "supplied range of [{}, {}] is not finite".format(first_edge, last_edge))
    elif a.size == 0:
        # handle empty arrays. Can't determine range, so use 0-1.
        first_edge, last_edge = 0, 1
    else:
        first_edge, last_edge = a.min(), a.max()
        if not (np.isfinite(first_edge) and np.isfinite(last_edge)):
            raise ValueError(
                "autodetected range of [{}, {}] is not finite".format(first_edge, last_edge))

    # expand empty range to avoid divide by zero
    if first_edge == last_edge:
        first_edge = first_edge - 0.5
        last_edge = last_edge + 0.5

    return first_edge, last_edge


def _unsigned_subtract(a, b):
    """
    Subtract two values where a >= b, and produce an unsigned result

    This is needed when finding the difference between the upper and lower
    bound of an int16 histogram

    Note: vendored from numpy.lib._histograms_impl
    """
    import numpy as np
    # coerce to a single type
    signed_to_unsigned = {
        np.byte: np.ubyte,
        np.short: np.ushort,
        np.intc: np.uintc,
        np.int_: np.uint,
        np.longlong: np.ulonglong
    }
    dt = np.result_type(a, b)
    try:
        unsigned_dt = signed_to_unsigned[dt.type]
    except KeyError:
        return np.subtract(a, b, dtype=dt)
    else:
        # we know the inputs are integers, and we are deliberately casting
        # signed to unsigned.  The input may be negative python integers so
        # ensure we pass in arrays with the initial dtype (related to NEP 50).
        return np.subtract(np.asarray(a, dtype=dt), np.asarray(b, dtype=dt),
                           casting='unsafe', dtype=unsigned_dt)


def _fill_missing_colors(label_to_color):
    """
    label_to_color = {'foo': kwimage.Color('red').as01(), 'bar': None}
    """
    from distinctipy import distinctipy
    import kwarray
    import numpy as np
    import kwimage
    given = {k: kwimage.Color(v).as01() for k, v in label_to_color.items() if v is not None}
    needs_color = sorted(set(label_to_color) - set(given))

    seed = 6777939437
    # hack in our code

    def _patched_get_random_color(pastel_factor=0, rng=None):
        rng = kwarray.ensure_rng(seed, api='python')
        color = [(rng.random() + pastel_factor) / (1.0 + pastel_factor) for _ in range(3)]
        return tuple(color)
    distinctipy.get_random_color = _patched_get_random_color

    exclude_colors = [
        tuple(map(float, (d, d, d)))
        for d in np.linspace(0, 1, 5)
    ] + list(given.values())

    final = given.copy()
    new_colors = distinctipy.get_colors(len(needs_color), exclude_colors=exclude_colors)
    for key, new_color in zip(needs_color, new_colors):
        final[key] = tuple(map(float, new_color))
    return final
