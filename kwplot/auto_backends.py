# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import os
import ubelt as ub


_qtensured = False


def _current_ipython_session():
    """
    Returns a reference to the current IPython session, if one is running
    """
    try:
        __IPYTHON__
    except NameError:
        return None
    else:
        # if ipython is None we must have exited ipython at some point
        import IPython
        ipython = IPython.get_ipython()
        return ipython


def _qtensure():
    """
    If you are in an IPython session, ensures that your backend is Qt.
    """
    global _qtensured
    if not _qtensured:
        ipython = _current_ipython_session()
        if ipython:
            if 'PyQt4' in sys.modules:
                ipython.magic('pylab qt4 --no-import-all')
                _qtensured = True
            else:
                ipython.magic('pylab qt5 --no-import-all')
                _qtensured = True


def _aggensure():
    """
    Ensures that you are in agg mode as long as IPython is not running

    This might help prevent errors in tmux like:
        qt.qpa.screen: QXcbConnection: Could not connect to display localhost:10.0
        Could not connect to any X display.
    """
    import matplotlib as mpl
    current_backend = mpl.get_backend()
    if current_backend != 'agg':
        ipython = _current_ipython_session()
        if not ipython:
            set_mpl_backend('agg')


def set_mpl_backend(backend, verbose=None):
    """
    Args:
        backend (str): name of backend to use (e.g. Agg, PyQt)
    """
    import matplotlib as mpl
    if verbose:
        print('set_mpl_backend backend={}'.format(backend))
    if backend.lower().startswith('qt'):
        # handle interactive qt case
        _qtensure()
    current_backend = mpl.get_backend()
    if verbose:
        print('* current_backend = {!r}'.format(current_backend))
    if backend != current_backend:
        # If we have already imported pyplot, then we need to use experimental
        # behavior. Otherwise, we can just set the backend.
        if 'matplotlib.pyplot' in sys.modules:
            from matplotlib import pyplot as plt
            if verbose:
                print('plt.switch_backend({!r})'.format(current_backend))
            plt.switch_backend(backend)
        else:
            if verbose:
                print('mpl.use({!r})'.format(backend))
            mpl.use(backend)
    else:
        if verbose:
            print('not changing backends')
    if verbose:
        print('* new_backend = {!r}'.format(mpl.get_backend()))


_AUTOMPL_WAS_RUN = False


def autompl(verbose=0, recheck=False):
    """
    Uses platform heuristics to automatically set the matplotlib backend.
    If no display is available it will be set to `agg`, otherwise we will try
    to use the cross-platform `Qt5Agg` backend.

    Args:
        verbose (int, default=0): verbosity level
        recheck (bool, default=False): if False, this function will not run if
            it has already been called (this can save a significant amount of
            time).

    References:
        https://stackoverflow.com/questions/637005/check-if-x-server-is-running
    """
    global _AUTOMPL_WAS_RUN
    if recheck or not _AUTOMPL_WAS_RUN:
        if verbose:
            print('AUTOMPL')
        if sys.platform.startswith('win32'):
            # TODO: something reasonable
            pass
        else:
            DISPLAY = os.environ.get('DISPLAY', '')
            if DISPLAY:
                # Check if we can actually connect to X
                # NOTE: this call takes a significant amount of time
                info = ub.cmd('xdpyinfo', shell=True)
                if verbose:
                    print('xdpyinfo-info = {}'.format(ub.repr2(info)))
                if info['ret'] != 0:
                    DISPLAY = None

            if verbose:
                print(' * DISPLAY = {!r}'.format(DISPLAY))

            if not DISPLAY:
                backend = 'agg'
            else:
                if ub.modname_to_modpath('PyQt5'):
                    try:
                        import PyQt5  # NOQA
                        from PyQt5 import QtCore  # NOQA
                    except ImportError:
                        backend = 'agg'
                    else:
                        backend = 'Qt5Agg'
                elif ub.modname_to_modpath('PyQt4'):
                    try:
                        import Qt4Agg  # NOQA
                        from PyQt4 import QtCore  # NOQA
                    except ImportError:
                        backend = 'agg'
                    else:
                        backend = 'Qt4Agg'
                else:
                    backend = 'agg'

            set_mpl_backend(backend, verbose=verbose)

        _AUTOMPL_WAS_RUN = True


def autoplt(verbose=0, recheck=False):
    """
    Like autompl, but also returns the `matplotlib.pyplot` module for
    convenience.
    """
    autompl(verbose=verbose, recheck=recheck)
    from matplotlib import pyplot as plt
    return plt
