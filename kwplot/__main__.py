
def main():
    """
    """
    import kwplot
    import sys
    import kwimage
    plt = kwplot.autoplt()
    fpath = sys.argv[1]
    imdata = kwimage.imread(fpath)

    imdata = kwimage.normalize_intensity(imdata)
    kwplot.imshow(imdata)

    plt.show()


if __name__ == '__main__':
    main()
