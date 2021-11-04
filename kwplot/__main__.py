
def main():
    import kwplot
    plt = kwplot.autoplt()
    import sys
    fpath = sys.argv[1]
    import kwimage
    imdata = kwimage.imread(fpath)

    plt.show()


if __name__ == '__main__':
    main()
