def test_imshow_cli_kwconf_flags():
    from kwplot.cli.main import ImshowCLI

    config = ImshowCLI.cli(
        argv=['demo.png', '--no-stats', '--robust=false'],
    )
    assert config.fpath == 'demo.png'
    assert config.stats is False
    assert config.robust is False


def test_gifify_kwconf_cli_values():
    from kwplot.cli.gifify import Gifify

    config = Gifify.cli(
        argv=['a.png', 'b.jpg', '--fps=3.5', '--max-width=640'],
    )
    assert config.image_list == ['a.png', 'b.jpg']
    assert config.frames_per_second == 3.5
    assert config.max_width == 640
    assert config.output == 'auto'
