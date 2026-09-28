import pytest


@pytest.fixture
def pyplot_without_ensure_unicode(monkeypatch):
    """Exercise plotting without relying on ubelt's deprecated text helper."""
    import matplotlib
    import ubelt

    matplotlib.use('Agg')
    from matplotlib import pyplot as plt

    monkeypatch.delattr(ubelt, 'ensure_unicode', raising=False)
    yield plt
    plt.close('all')


@pytest.mark.parametrize('as_bytes', [False, True])
def test_set_figtitle_without_ensure_unicode(
        pyplot_without_ensure_unicode, as_bytes):
    import kwplot

    title = 'Résumé'
    subtitle = 'σ = 1'
    fig = pyplot_without_ensure_unicode.figure()
    kwplot.set_figtitle(
        title.encode('utf8') if as_bytes else title,
        subtitle=subtitle.encode('utf8') if as_bytes else subtitle,
        fig=fig,
    )
    assert fig._suptitle.get_text() == title + '\n' + subtitle
    fig.canvas.draw()


@pytest.mark.parametrize('as_bytes', [False, True])
def test_multi_plot_without_ensure_unicode(
        pyplot_without_ensure_unicode, as_bytes):
    import kwplot

    labels = {'title': 'Résumé', 'xlabel': 'époche', 'ylabel': 'σ'}
    inputs = {key: value.encode('utf8') if as_bytes else value
              for key, value in labels.items()}
    fig, ax = pyplot_without_ensure_unicode.subplots()
    kwplot.multi_plot([0, 1], [1, 2], ax=ax, **inputs)
    assert ax.get_title() == labels['title']
    assert ax.get_xlabel() == labels['xlabel']
    assert ax.get_ylabel() == labels['ylabel']
    fig.canvas.draw()


def test_none_plot_text_without_ensure_unicode(pyplot_without_ensure_unicode):
    import kwplot

    fig, ax = pyplot_without_ensure_unicode.subplots()
    kwplot.set_figtitle(None, fig=fig)
    assert fig._suptitle.get_text() == ''
    kwplot.multi_plot([0, 1], [1, 2], ax=ax,
                      title=None, xlabel=None, ylabel=None)
    assert ax.get_title() == ''
    assert ax.get_xlabel() == ''
    assert ax.get_ylabel() == ''
    fig.canvas.draw()
