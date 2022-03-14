
def main():
    """

    """
    import kwplot
    import sys
    import ubelt as ub
    import kwimage
    import kwarray
    plt = kwplot.autoplt()
    fpath = sys.argv[1]
    print('read fpath = {!r}'.format(fpath))
    imdata = kwimage.imread(fpath, nodata='float')

    print('imdata.dtype = {!r}'.format(imdata.dtype))
    print('imdata.shape = {!r}'.format(imdata.shape))

    stats = kwarray.stats_dict(imdata, nan=True)
    print('stats = {}'.format(ub.repr2(stats, nl=1)))

    if kwimage.num_channels(imdata) == 2:
        import numpy as np
        # hack for a 3rd channel
        imdata = np.concatenate([imdata, np.zeros_like(imdata)[..., 0:1]], axis=2)

    imdata = kwarray.atleast_nd(imdata, 3)[..., 0:3]

    print('normalize')
    imdata = kwimage.normalize_intensity(imdata)

    print('showing')
    from os.path import basename
    kwplot.imshow(imdata, title=basename(fpath))

    plt.show()


if __name__ == '__main__':
    main()
