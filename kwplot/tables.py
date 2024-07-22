import ubelt as ub


def dataframe_table(table, fpath, title=None, fontsize=12,
                    table_conversion='auto', dpi=None, fnum=None, show=False):
    """
    Use dataframe_image (dfi) to render a pandas dataframe.

    Args:
        table (pandas.DataFrame | pandas.io.formats.style.Styler)

        fpath (str | PathLike): where to save the image

        table_conversion (str):
            can be auto, chrome, or matplotlib (auto tries to default to
            chrome)

    Example:
        >>> # xdoctest: +REQUIRES(module:dataframe_image)
        >>> from geowatch.utils.util_kwplot import *  # NOQA
        >>> import ubelt as ub
        >>> dpath = ub.Path.appdir('kwplot/tests/test_dfi').ensuredir()
        >>> import pandas as pd
        >>> table = pd.DataFrame({'foo': ['one', 'one', 'one', 'two', 'two', 'two'],
        ...                       'bar': ['A', 'B', 'C', 'A', 'B', 'C'],
        ...                       'baz': [1, 2, 3, 4, 5, 6],
        ...                       'zoo': ['x', 'y', 'z', 'q', 'w', 't']})
        >>> fpath = dpath / 'dfi.png'
        >>> dataframe_table(table, fpath, title='A caption / title')
    """
    import kwimage
    import kwplot
    import dataframe_image as dfi
    import pandas as pd
    # table_conversion = "chrome"  # matplotlib

    # print(f'table_conversion={table_conversion}')
    if table_conversion == 'auto':
        if ub.find_exe('google-chrome'):
            table_conversion = 'chrome'
        else:
            table_conversion = 'matplotlib'

    if isinstance(table, pd.DataFrame):
        style = table.style
    else:
        style = table

    if title is not None:
        style = style.set_caption(title)

    # print(f'table_conversion={table_conversion}')
    dfi.export(
        style,
        str(fpath),
        table_conversion=table_conversion,
        fontsize=fontsize,
        max_rows=-1,
        dpi=dpi,
    )
    if show == 'imshow':
        imdata = kwimage.imread(fpath)
        kwplot.imshow(imdata, fnum=fnum)
    elif show == 'eog':
        import xdev
        xdev.startfile(fpath)
    elif show:
        raise KeyError(f'Show can be "imshow" or "eog", not {show!r}')


def humanize_dataframe(df, col_formats=None, human_labels=None, index_format=None,
                       title=None):
    import humanize
    df2 = df.copy()
    if col_formats is not None:
        for col, fmt in col_formats.items():
            if fmt == 'intcomma':
                df2[col] = df[col].apply(humanize.intcomma)
            if fmt == 'concice_si_display':
                from kwcoco.metrics.drawing import concice_si_display
                for row in df2.index:
                    val = df2.loc[row, col]
                    # if isinstance(val, str):
                    #     try:
                    #         val = float(val)
                    #     except Exception:
                    #         ...
                    # print(f'val: {type(val)}={val}')
                    if isinstance(val, float):
                        val = concice_si_display(val)
                        df2.loc[row, col] = val
                df2[col] = df[col].apply(humanize.intcomma)
            if callable(fmt):
                df2[col] = df[col].apply(fmt)
    if human_labels:
        df2 = df2.rename(human_labels, axis=1)

    indexes = [df2.index, df2.columns]
    if human_labels:

        for index in indexes:
            if index.name is not None:
                index.name = human_labels.get(index.name, index.name)
            if index.names:
                index.names = [human_labels.get(n, n) for n in index.names]

    if index_format == 'capcase':
        def capcase(x):
            if '_' in x or x.islower():
                return ' '.join([w.capitalize() for w in x.split('_')])
            return x
        df2.index.values[:] = [human_labels.get(x, x) for x in df2.index.values]
        df2.index.values[:] = list(map(capcase, df2.index.values))
        # human_df = human_df.applymap(lambda x: str(x) if isinstance(x, int) else '{:0.2f}'.format(x))
        pass

    df2_style = df2.style
    if title:
        df2_style = df2_style.set_caption(title)
    return df2_style
