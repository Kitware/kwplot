
def main():
    """
    """
    import kwplot
    import sys
    import kwimage
    plt = kwplot.autoplt()
    fpath = sys.argv[1]
    print('read fpath = {!r}'.format(fpath))
    imdata = kwimage.imread(fpath)
    print('imdata.dtype = {!r}'.format(imdata.dtype))
    print('imdata.shape = {!r}'.format(imdata.shape))
    print('normalize')
    imdata = kwimage.normalize_intensity(imdata)
    print('showing')
    kwplot.imshow(imdata)

    plt.show()


if __name__ == '__main__':
    main()
