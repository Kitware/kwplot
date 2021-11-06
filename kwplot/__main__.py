
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
    imdata = kwimage.imread(fpath)

    print('imdata.dtype = {!r}'.format(imdata.dtype))
    print('imdata.shape = {!r}'.format(imdata.shape))

    stats = kwarray.stats_dict(imdata)
    print('stats = {}'.format(ub.repr2(stats, nl=1)))

    print('normalize')
    imdata = kwimage.normalize_intensity(imdata, nodata=0)

    print('showing')
    from os.path import basename
    kwplot.imshow(imdata, title=basename(fpath))

    plt.show()


if __name__ == '__main__':
    main()
