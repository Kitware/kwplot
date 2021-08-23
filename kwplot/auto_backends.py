# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import os
import ubelt as ub

__all__ = [
    'autompl', 'autoplt', 'autosns', 'set_mpl_backend', 'BackendContext',
]


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


def autompl(verbose=0, recheck=False, force=None):
    """
    Uses platform heuristics to automatically set the matplotlib backend.
    If no display is available it will be set to `agg`, otherwise we will try
    to use the cross-platform `Qt5Agg` backend.

    Args:
        verbose (int, default=0): verbosity level
        recheck (bool, default=False): if False, this function will not run if
            it has already been called (this can save a significant amount of
            time).
        force (str, default=None): backend to force to or "auto"

    Checks:
        export QT_DEBUG_PLUGINS=1
        xdoctest -m kwplot.auto_backends autompl --check
        KWPLOT_UNSAFE=1 xdoctest -m kwplot.auto_backends autompl --check
        KWPLOT_UNSAFE=0 xdoctest -m kwplot.auto_backends autompl --check

    Example:
        >>> # xdoctest +REQUIRES(--check)
        >>> plt = autoplt(verbose=1)
        >>> plt.figure()

    References:
        https://stackoverflow.com/questions/637005/check-if-x-server-is-running
    """
    global _AUTOMPL_WAS_RUN
    if force == 'auto':
        recheck = True
        force = None
    elif force is not None:
        set_mpl_backend(force)
        _AUTOMPL_WAS_RUN = True

    if recheck or not _AUTOMPL_WAS_RUN:
        if verbose:
            print('AUTOMPL')
        if sys.platform.startswith('win32'):
            # TODO: something reasonable
            pass
        else:
            DISPLAY = os.environ.get('DISPLAY', '')
            if DISPLAY:
                if sys.platform.startswith('linux') and ub.find_exe('xdpyinfo'):
                    # On Linux, check if we can actually connect to X
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
                """
                Note:

                    May encounter error that crashes the program, not sure why
                    this happens yet. The current workaround is to uninstall
                    PyQt5, but that isn't sustainable.

                    QObject::moveToThread: Current thread (0x7fe8d965d030) is not the object's thread (0x7fffb0f64340).
                    Cannot move to target thread (0x7fe8d965d030)


                    qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
                    This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

                    Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.


                UPDATE 2021-01-04:

                    By setting

                    export QT_DEBUG_PLUGINS=1

                    I was able to look at more debug information. It turns out
                    that it was grabbing the xcb plugin from the opencv-python
                    package. I uninstalled that package and then installed
                    opencv-python-headless which does not include an xcb
                    binary. However, now the it is missing "libxcb-xinerama".

                    May be able to do something with:
                        conda install -c conda-forge xorg-libxinerama

                        # But that didnt work I had to
                        pip uninstall PyQt5

                        # This seems to work correctly
                        conda install -c anaconda pyqt
                """
                if ub.modname_to_modpath('PyQt5'):
                    try:
                        import PyQt5  # NOQA
                        from PyQt5 import QtCore  # NOQA
                    except ImportError:
                        backend = 'agg'
                    else:
                        backend = 'Qt5Agg'

                        KWPLOT_UNSAFE = os.environ.get('KWPLOT_UNSAFE', '')
                        TRY_AVOID_CRASH = KWPLOT_UNSAFE.lower() not in ['1', 'true', 'yes']

                        if TRY_AVOID_CRASH and ub.LINUX:
                            # HOLD UP. Lets try to avoid a crash.
                            if 'cv2' in sys.modules:
                                from os.path import dirname, join, exists
                                cv2 = sys.modules['cv2']
                                cv2_mod_dpath = dirname(cv2.__file__)
                                cv2_lib_dpath = join(cv2_mod_dpath, 'qt/plugins/platforms')
                                cv2_qxcb_fpath = join(cv2_lib_dpath, 'libqxcb.so')

                                qt_mod_dpath = dirname(QtCore.__file__)
                                qt_lib_dpath = join(qt_mod_dpath, 'Qt/plugins/platforms')
                                qt_qxcb_fpath = join(qt_lib_dpath, 'libqxcb.so')

                                if exists(cv2_qxcb_fpath) and exists(qt_qxcb_fpath):
                                    # Can we use ldd to make the test better?
                                    import warnings
                                    warnings.warn(ub.paragraph(
                                        '''
                                        Autompl has detected libqxcb in PyQt
                                        and cv2.  Falling back to agg to avoid
                                        a potential crash. This can be worked
                                        around by installing
                                        opencv-python-headless instead of
                                        opencv-python.

                                        Disable this check by setting the
                                        environ KWPLOT_UNSAFE=1
                                        '''
                                    ))
                                    backend = 'agg'

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

        if 0:
            # TODO:
            # IF IN A NOTEBOOK, BE SURE TO SET INLINE BEHAVIOR
            # THIS EFFECTIVELY REPRODUCES THE %matplotlib inline behavior
            # BUT USING AN ACTUAL PYTHON FUNCTION
            shell = _current_ipython_session()
            if shell:
                shell.enable_matplotlib('inline')

        _AUTOMPL_WAS_RUN = True


def autoplt(verbose=0, recheck=False):
    """
    Like autompl, but also returns the `matplotlib.pyplot` module for
    convenience.
    """
    autompl(verbose=verbose, recheck=recheck)
    from matplotlib import pyplot as plt
    return plt


def autosns(verbose=0, recheck=False):
    """
    Like autosns, but also calls `seaborn.set` and returns the `seaborn` module
    for convenience.
    """
    autompl(verbose=verbose, recheck=recheck)
    import seaborn as sns
    sns.set()
    return sns


class BackendContext(object):
    """
    Context manager that ensures a specific backend, but then reverts after the
    context has ended.

    Checks:
        xdoctest -m kwplot.auto_backends BackendContext --check

    Example:
        >>> # xdoctest +REQUIRES(--check)
        >>> from kwplot.auto_backends import *  # NOQA
        >>> import matplotlib as mpl
        >>> import kwplot
        >>> print(mpl.get_backend())
        >>> #kwplot.autompl(force='auto')
        >>> #print(mpl.get_backend())
        >>> #fig1 = kwplot.figure(fnum=3)
        >>> #print(mpl.get_backend())
        >>> with BackendContext('agg'):
        >>>     print(mpl.get_backend())
        >>>     fig2 = kwplot.figure(fnum=4)
        >>> print(mpl.get_backend())
    """

    def __init__(self, backend):
        self.backend = backend
        self.prev = None
        self._prev_backend_was_loaded = 'matplotlib.pyplot' in sys.modules

    def __enter__(self):
        import matplotlib as mpl
        self.prev = mpl.get_backend()

        if self.prev == 'Qt5Agg':
            # Hack for the case where our default matplotlib backend is Qt5Agg
            # but we don't have Qt bindings available. (I think this may be a
            # configuration error on my part). Either way, its easy to test for
            # and fix. If the default backend is Qt5Agg, but importing the
            # bindings causes an error, just set the default to agg, which will
            # supress the warnings.
            try:
                from matplotlib.backends.qt_compat import QtGui  # NOQA
            except ImportError:
                # TODO: should we try this instead?
                # mpl.rcParams['backend_fallback']
                self.prev = 'agg'

        set_mpl_backend(self.backend)

    def __exit__(self, *args):
        if self.prev is not None:
            """
            Note: 2021-01-07
                Running on in an ssh-session (where in this case ssh did
                not have an X server, but an X server was running
                elsewhere) we got this error.

                ImportError: Cannot load backend 'Qt5Agg' which requires the
                'qt5' interactive framework, as 'headless' is currently running

                when using BackendContext('agg')

                This is likely because the default was Qt5Agg, but it was not
                loaded. We switched to agg just fine, but when we switched back
                it tried to load Qt5Agg, which was not available and thus it
                failed.
            """
            try:
                # Note
                set_mpl_backend(self.prev)
            except Exception:
                if self._prev_backend_was_loaded:
                    # Only propogate the error if we had explicitly used pyplot
                    # beforehand. Note sure if this is the right thing to do.
                    raise
