# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import numpy as np
import six


class PlotNums(object):
    """
    Convinience class for dealing with plot numberings (pnums)

    Example:
        >>> import ubelt as ub
        >>> pnum_ = PlotNums(nRows=2, nCols=2)
        >>> # Indexable
        >>> print(pnum_[0])
        (2, 2, 1)
        >>> # Iterable
        >>> print(ub.repr2(list(pnum_), nl=0, nobr=True))
        (2, 2, 1), (2, 2, 2), (2, 2, 3), (2, 2, 4)
        >>> # Callable (iterates through a default iterator)
        >>> print(pnum_())
        (2, 2, 1)
        >>> print(pnum_())
        (2, 2, 2)
    """

    def __init__(self, nRows=None, nCols=None, nSubplots=None, start=0):
        nRows, nCols = self._get_num_rc(nSubplots, nRows, nCols)
        self.nRows = nRows
        self.nCols = nCols
        base = 0
        self.offset = 0 if base == 1 else 1
        self.start = start
        self._iter = None

    def __getitem__(self, px):
        return (self.nRows, self.nCols, px + self.offset)

    def __call__(self):
        """
        replacement for make_pnum_nextgen

        Example:
            >>> import ubelt as ub
            >>> import itertools as it
            >>> pnum_ = PlotNums(nSubplots=9)
            >>> pnum_list = [pnum_() for _ in range(len(pnum_))]
            >>> result = ('pnum_list = %s' % (ub.repr2(pnum_list),))
            >>> print(result)

        Example:
            >>> import ubelt as ub
            >>> import itertools as it
            >>> for nRows, nCols, nSubplots in it.product([None, 3], [None, 3], [None, 9]):
            >>>     start = 0
            >>>     pnum_ = PlotNums(nRows, nCols, nSubplots, start)
            >>>     pnum_list = [pnum_() for _ in range(len(pnum_))]
            >>>     print((nRows, nCols, nSubplots))
            >>>     result = ('pnum_list = %s' % (ub.repr2(pnum_list),))
            >>>     print(result)
        """
        if self._iter is None:
            self._iter = iter(self)
        return six.next(self._iter)

    def __iter__(self):
        r"""
        Yields:
            tuple : pnum

        Example:
            >>> import ubelt as ub
            >>> pnum_ = iter(PlotNums(nRows=3, nCols=2))
            >>> result = ub.repr2(list(pnum_), nl=1, nobr=True)
            >>> print(result)
            (3, 2, 1),
            (3, 2, 2),
            (3, 2, 3),
            (3, 2, 4),
            (3, 2, 5),
            (3, 2, 6),

        Example:
            >>> import ubelt as ub
            >>> nRows = 3
            >>> nCols = 2
            >>> pnum_ = iter(PlotNums(nRows, nCols, start=3))
            >>> result = ub.repr2(list(pnum_), nl=1, nobr=True)
            >>> print(result)
            (3, 2, 4),
            (3, 2, 5),
            (3, 2, 6),
        """
        for px in range(self.start, len(self)):
            yield self[px]

    def __len__(self):
        total_plots = self.nRows * self.nCols
        return total_plots

    @classmethod
    def _get_num_rc(PlotNums, nSubplots=None, nRows=None, nCols=None):
        r"""
        Gets a constrained row column plot grid

        Args:
            nSubplots (None): (default = None)
            nRows (None): (default = None)
            nCols (None): (default = None)

        Returns:
            tuple: (nRows, nCols)

        Example:
            >>> import ubelt as ub
            >>> cases = [
            >>>     dict(nRows=None, nCols=None, nSubplots=None),
            >>>     dict(nRows=2, nCols=None, nSubplots=5),
            >>>     dict(nRows=None, nCols=2, nSubplots=5),
            >>>     dict(nRows=None, nCols=None, nSubplots=5),
            >>> ]
            >>> for kw in cases:
            >>>     print('----')
            >>>     size = PlotNums._get_num_rc(**kw)
            >>>     if kw['nSubplots'] is not None:
            >>>         assert size[0] * size[1] >= kw['nSubplots']
            >>>     print('**kw = %s' % (ub.repr2(kw),))
            >>>     print('size = %r' % (size,))
        """
        if nSubplots is None:
            if nRows is None:
                nRows = 1
            if nCols is None:
                nCols = 1
        else:
            if nRows is None and nCols is None:
                nRows, nCols = PlotNums._get_square_row_cols(nSubplots)
            elif nRows is not None:
                nCols = int(np.ceil(nSubplots / nRows))
            elif nCols is not None:
                nRows = int(np.ceil(nSubplots / nCols))
        return nRows, nCols

    @staticmethod
    def _get_square_row_cols(nSubplots, max_cols=None, fix=False, inclusive=True):
        r"""
        Args:
            nSubplots (int):
            max_cols (int):

        Returns:
            tuple: (int, int)

        Example:
            >>> nSubplots = 9
            >>> nSubplots_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            >>> max_cols = None
            >>> rc_list = [PlotNums._get_square_row_cols(nSubplots, fix=True) for nSubplots in nSubplots_list]
            >>> print(repr(np.array(rc_list).T))
            array([[1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3],
                   [1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4]])
        """
        if nSubplots == 0:
            return 0, 0
        if inclusive:
            rounder = np.ceil
        else:
            rounder = np.floor
        if fix:
            # This function is very broken, but it might have dependencies
            # this is the correct version
            nCols = int(rounder(np.sqrt(nSubplots)))
            nRows = int(rounder(nSubplots / nCols))
            return nRows, nCols
        else:
            # This is the clamped num cols version
            # probably used in ibeis.viz
            if max_cols is None:
                max_cols = 5
                if nSubplots in [4]:
                    max_cols = 2
                if nSubplots in [5, 6, 7]:
                    max_cols = 3
                if nSubplots in [8]:
                    max_cols = 4
            nCols = int(min(nSubplots, max_cols))
            #nCols = int(min(rounder(np.sqrt(nrids)), 5))
            nRows = int(rounder(nSubplots / nCols))
        return nRows, nCols
