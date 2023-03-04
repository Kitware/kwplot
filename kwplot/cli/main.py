#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
A simple CLI for helping with plotting and viewing tasks
"""
import ubelt as ub
from scriptconfig.modal import ModalCLI
from scriptconfig import DataConfig, Value


modal = ModalCLI(description=ub.codeblock(
    '''
    The Kitware Plot CLI

    A collection of excellent developer tools for excellent developers.
    '''))


@modal
class ImshowCLI(DataConfig):
    """
    Plot an image with matplotlib using robust normalization by default.

    Example:
        FPATH=$(python -c "import kwimage; print(kwimage.grab_test_image_fpath('amazon'))")
        echo $FPATH
        kwplot imshow --fpath=$HOME/.cache/kwimage/demodata/amazon.jpg
        kwplot imshow --fpath=$HOME/.cache/kwimage/demodata/amazon.jpg --no-stats --no-robust
        kwplot $HOME/.cache/kwimage/demodata/amazon.jpg
    """
    __command__ = 'imshow'

    fpath = Value(None, position=1, help='path to the image to visualize')
    robust = Value(True, isflag=True, help='robustly normlizes the image intensity')
    stats = Value(True, isflag=True, help='if False does not compute stats')

    @classmethod
    def main(cls, cmdline=False, **kwargs):
        config = cls.cli(cmdline=cmdline, data=kwargs)
        print('config = {}'.format(ub.urepr(dict(config), nl=1)))
        import kwimage
        import kwarray
        import kwplot
        plt = kwplot.autoplt()
        fpath = config.fpath
        print('read fpath = {!r}'.format(fpath))
        imdata = kwimage.imread(fpath, nodata='float')

        print('imdata.dtype = {!r}'.format(imdata.dtype))
        print('imdata.shape = {!r}'.format(imdata.shape))

        if config.stats:
            stats = kwarray.stats_dict(imdata, nan=True)
            print('stats = {}'.format(ub.repr2(stats, nl=1)))

        if kwimage.num_channels(imdata) == 2:
            import numpy as np
            # hack for a 3rd channel
            imdata = np.concatenate([imdata, np.zeros_like(imdata)[..., 0:1]], axis=2)

        imdata = kwarray.atleast_nd(imdata, 3)[..., 0:3]

        if config.robust:
            print('normalize')
            imdata = kwimage.normalize_intensity(imdata)

        imdata = kwimage.fill_nans_with_checkers(imdata, on_value=0.3)

        print('showing')
        from os.path import basename
        kwplot.imshow(imdata, title=basename(fpath))

        plt.show()


def main():
    import sys
    import os
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        # NON MODAL CASE RUNS IMSHOW
        ImshowCLI.main(cmdline=0, fpath=sys.argv[1])
        ...
    else:
        from kwplot.cli import gifify
        modal.register(gifify.Gifify)

        modal.run()


if __name__ == '__main__':
    """
    CommandLine:
        kwplot --help
        "
    """
    main()
