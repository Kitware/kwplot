"""
This module handles automatically determening a "good" matplotlib backend to
use before importing pyplot.
"""
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
            else:
                if hasattr(ipython, 'run_line_magic'):
                    # For IPython >= 8.1
                    ipython.run_line_magic('matplotlib', 'qt')
                else:
                    # `magic(...)` is deprecated since IPython 0.13
                    ipython.magic('%matplotlib qt')
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


def set_mpl_backend(backend, verbose=0):
    """
    Args:
        backend (str): name of backend as string that :func:`matplotlib.use`
            would accept (e.g. Agg or Qt5Agg).

        verbose (int, default=0):
            verbosity level
    """
    import matplotlib as mpl
    if verbose:
        print('[kwplot.set_mpl_backend] backend={}'.format(backend))
    if backend.lower().startswith('qt'):
        # handle interactive qt case
        _qtensure()
    current_backend = mpl.get_backend()
    if verbose:
        mpl_config_fpath = mpl.matplotlib_fname()
        print('[kwplot.set_mpl_backend] mpl config file={}'.format(mpl_config_fpath))
        print('[kwplot.set_mpl_backend] current_backend = {!r}'.format(current_backend))
    if backend != current_backend:
        # If we have already imported pyplot, then we need to use experimental
        # behavior. Otherwise, we can just set the backend.
        if 'matplotlib.pyplot' in sys.modules:
            from matplotlib import pyplot as plt
            if verbose:
                print('[kwplot.set_mpl_backend] plt.switch_backend({!r})'.format(current_backend))
            plt.switch_backend(backend)
        else:
            if verbose:
                print('[kwplot.set_mpl_backend] mpl.use({!r})'.format(backend))
            mpl.use(backend)
    else:
        if verbose:
            print('[kwplot.set_mpl_backend] not changing backends')
    if verbose:
        print('[kwplot.set_mpl_backend] new_backend = {!r}'.format(mpl.get_backend()))


_AUTOMPL_WAS_RUN = False


def autompl(verbose=0, recheck=False, force=None):
    """
    Uses platform heuristics to automatically set the matplotlib backend.
    If no display is available it will be set to `agg`, otherwise we will try
    to use the cross-platform `Qt5Agg` backend.

    Args:
        verbose (int):
            verbosity level

        recheck (bool):
            if False, this function will not run if it has already been called
            (this can save a significant amount of time).

        force (str | int | None):
            If None or "auto", then the backend will only be set if this
            function has not been run before. Otherwise it will be set to the
            chosen backend, which is a string that :func:`matplotlib.use` would
            accept (e.g. Agg or Qt5Agg).

    CommandLine:
        # Checks
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
        https://matplotlib.org/stable/users/explain/figure/backends.html
    """
    global _AUTOMPL_WAS_RUN
    if verbose > 2:
        print('[kwplot.autompl] Called autompl')

    if force == 'auto':
        recheck = True
        force = None
    elif force is not None:
        _run_inline_magic_in_colab(verbose)
        set_mpl_backend(force, verbose=verbose)
        _AUTOMPL_WAS_RUN = True

    if recheck or not _AUTOMPL_WAS_RUN:
        _run_inline_magic_in_colab(verbose)
        backend = _determine_best_backend(verbose=verbose)
        if backend is not None:
            set_mpl_backend(backend, verbose=verbose)

        _AUTOMPL_WAS_RUN = True
    else:
        if verbose > 2:
            print('[kwplot.autompl] Check already ran and recheck=False. Skipping')


def _run_inline_magic_in_colab(verbose):
    # If in a colab notebook, be sure to set inline behavior this
    # effectively reproduces the %matplotlib inline behavior but using
    # an actual python function.
    ipy = _current_ipython_session()
    if ipy:
        if 'colab' in str(ipy.config['IPKernelApp']['kernel_class']):
            if verbose:
                print('Detected colab, running inline ipython magic')
            ipy.run_line_magic('matplotlib', 'inline')


def _determine_best_backend(verbose):
    """
    Helper to determine what a good backend would be for autompl
    """
    if verbose:
        print('[kwplot.autompl] Attempting to determening best backend')

    if sys.platform.startswith('win32'):
        if verbose:
            # TODO something reasonable
            print('[kwplot.autompl] No heuristics implemented on windows')
        return None

    backend_infos = {}
    backend_infos['pyqt6'] = {'usable': None}
    backend_infos['pyqt5'] = {'usable': None}
    backend_infos['pyqt4'] = {'usable': None}

    DISPLAY = os.environ.get('DISPLAY', '')
    if DISPLAY:
        if sys.platform.startswith('linux') and ub.find_exe('xdpyinfo'):
            # On Linux, check if we can actually connect to X
            # NOTE: this call takes a significant amount of time
            info = ub.cmd('xdpyinfo', shell=True)
            if verbose > 3:
                print('xdpyinfo-info = {}'.format(ub.repr2(info)))
            if info['ret'] != 0:
                DISPLAY = None

    if verbose:
        print('[kwplot.autompl] DISPLAY = {!r}'.format(DISPLAY))

    if not DISPLAY:
        if verbose:
            print('[kwplot.autompl] No display, agg is probably best')
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

        UPDATE 2024-08-11:

             For PyQt6, I got the error message:
                 "From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load
                 the Qt xcb platform plugin."

             And was able to resolve it by installing a system library:

                 sudo apt-get install -y libxcb-cursor-dev
        """

        # Enumerate backends and candidate module paths that might exist
        backend_infos['pyqt6']['modpath'] = ub.modname_to_modpath('PyQt6')
        backend_infos['pyqt5']['modpath'] = ub.modname_to_modpath('PyQt5')
        backend_infos['pyqt4']['modpath'] = ub.modname_to_modpath('PyQt4')

        for k, info in backend_infos.items():
            if info['modpath'] is None:
                info['usable'] = False

        if backend_infos['pyqt6']['modpath']:
            try:
                import PyQt6  # NOQA
                from PyQt6 import QtCore  # NOQA
            except ImportError as ex:
                if verbose:
                    print('[kwplot.autompl] No PyQt6, agg is probably best')
                backend_infos['pyqt6']['usable'] = False
                backend_infos['pyqt6']['importable'] = False
                backend_infos['pyqt6']['import_error'] = repr(ex)
            else:
                backend_infos['pyqt6']['usable'] = True
                backend_infos['pyqt6']['importable'] = True
                KWPLOT_UNSAFE = os.environ.get('KWPLOT_UNSAFE', '')
                TRY_AVOID_CRASH = KWPLOT_UNSAFE.lower() not in ['1', 'true', 'yes']
                if TRY_AVOID_CRASH and ub.LINUX:
                    # HOLD UP. Lets try to avoid a crash.
                    if _check_for_linux_opencv_qt_conflicts(QtCore):
                        backend_infos['pyqt6']['usable'] = False
        elif backend_infos['pyqt5']['modpath']:
            try:
                import PyQt5  # NOQA
                from PyQt5 import QtCore  # NOQA
            except ImportError as ex:
                if verbose:
                    print('[kwplot.autompl] No PyQt5, agg is probably best')
                backend_infos['pyqt5']['usable'] = False
                backend_infos['pyqt5']['importable'] = False
                backend_infos['pyqt5']['import_error'] = repr(ex)
            else:
                backend_infos['pyqt5']['usable'] = True
                backend_infos['pyqt5']['importable'] = True
                KWPLOT_UNSAFE = os.environ.get('KWPLOT_UNSAFE', '')
                TRY_AVOID_CRASH = KWPLOT_UNSAFE.lower() not in ['1', 'true', 'yes']
                if TRY_AVOID_CRASH and ub.LINUX:
                    # HOLD UP. Lets try to avoid a crash.
                    if _check_for_linux_opencv_qt_conflicts(QtCore):
                        backend_infos['pyqt5']['usable'] = False
        elif backend_infos['pyqt4']['modpath']:
            try:
                import Qt4Agg  # NOQA
                from PyQt4 import QtCore  # NOQA
            except ImportError as ex:
                backend_infos['pyqt4']['usable'] = False
                backend_infos['pyqt4']['importable'] = False
                backend_infos['pyqt4']['import_error'] = repr(ex)
            else:
                backend_infos['pyqt4']['importable'] = True
                backend_infos['pyqt4']['usable'] = True

    if backend_infos['pyqt6']['usable']:
        backend = 'QtAgg'
    elif backend_infos['pyqt5']['usable']:
        backend = 'Qt5Agg'
    elif backend_infos['pyqt4']['usable']:
        backend = 'Qt4Agg'
    else:
        backend = 'agg'

    if verbose:
        if verbose > 1:
            print(f'backend_infos = {ub.urepr(backend_infos, nl=1)}')
        print('[kwplot.autompl] Determined best backend is probably backend={}'.format(backend))
    return backend


def _check_for_linux_opencv_qt_conflicts(QtCore):
    """
    See if there are conflicting shared object files for qt
    """
    if 'cv2' in sys.modules:
        cv2 = sys.modules['cv2']
        cv2_mod_fpath = ub.Path(cv2.__file__)
        cv2_mod_dpath = cv2_mod_fpath.parent
        cv2_lib_dpath = cv2_mod_dpath / 'qt/plugins/platforms'
        cv2_qxcb_fpath = cv2_lib_dpath / 'libqxcb.so'

        qt_mod_fpath = ub.Path(QtCore.__file__)
        qt_mod_dpath = qt_mod_fpath.parent
        qt_lib_dpath = qt_mod_dpath / 'Qt/plugins/platforms'
        qt_qxcb_fpath = qt_lib_dpath / 'libqxcb.so'

        if cv2_qxcb_fpath.exists() and qt_qxcb_fpath.exists():
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
            return True
    return False


def _check_for_cv2_qt_incompat():
    import cv2
    import ubelt as ub
    from PyQt5 import QtCore  # NOQA

    cv2_mod_dpath = ub.Path(cv2.__file__).parent
    cv2_lib_dpath = ub.Path(cv2_mod_dpath) / 'qt/plugins/platforms'
    cv2_qxcb_fpath = ub.Path(cv2_lib_dpath) / 'libqxcb.so'

    qt_mod_dpath = ub.Path(QtCore.__file__).parent
    qt_lib_dpath1 = qt_mod_dpath / 'Qt/plugins/platforms'
    qt_lib_dpath2 = (qt_mod_dpath / 'Qt5/plugins/platforms')
    if qt_lib_dpath1.exists():
        qt_lib_dpath = qt_lib_dpath1
    elif qt_lib_dpath2.exists():
        qt_lib_dpath = qt_lib_dpath2
    else:
        raise OSError('cannot find qt library directory')
    qt_qxcb_fpath = qt_lib_dpath / 'libqxcb.so'

    cv2_qxb_exist = cv2_qxcb_fpath.exists()
    qt_qxb_exist = qt_qxcb_fpath.exists()
    print(f'cv2_qxb_exist={cv2_qxb_exist}')
    print(f'qt_qxb_exist={qt_qxb_exist}')


def autoplt(verbose=0, recheck=False, force=None):
    """
    Like :func:`kwplot.autompl`, but also returns the
    :mod:`matplotlib.pyplot` module for convenience.

    See :func:`kwplot.auto_backends.autompl` for argument details

    Note:
        In Python 3.7 accessing ``kwplot.plt`` or ``kwplot.pyplot`` lazily
        calls this function.

    Returns:
        ModuleType
    """
    autompl(verbose=verbose, recheck=recheck, force=force)
    from matplotlib import pyplot as plt
    return plt


def autosns(verbose=0, recheck=False, force=None):
    """
    Like :func:`kwplot.autompl`, but also calls
    :func:`seaborn.set` and returns the :mod:`seaborn` module for convenience.

    See :func:`kwplot.auto_backends.autompl` for argument details

    Note:
        In Python 3.7 accessing ``kwplot.sns`` or ``kwplot.seaborn`` lazily
        calls this function.

    Returns:
        ModuleType
    """
    autompl(verbose=verbose, recheck=recheck, force=force)
    import seaborn as sns
    sns.set()
    return sns


class BackendContext:
    """
    Context manager that ensures a specific backend, but then reverts after the
    context has ended.

    Because this changes the backend after pyplot has initialized, there is a
    chance for odd behavior to occur. Please submit and issue if you experience
    this and can document the environment that caused it.

    CommandLine:
        # Checks
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

    def __init__(self, backend, strict=False):
        """
        Args:
            backend (str):
                the name of the backend to use in this context
                (e.g. Agg).

            strict (bool):
                if True, does not supress any error if attempting to return to
                the previous backend fails. Defaults to False.
        """
        self.backend = backend
        self.prev = None
        self._prev_backend_was_loaded = 'matplotlib.pyplot' in sys.modules
        self.strict = strict

    def __enter__(self):
        import matplotlib as mpl
        self.prev = mpl.get_backend()

        if self.prev in {'Qt5Agg', 'QtAgg'}:
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

            Note: 2024-08-27
                Got this error again when running in a slurm context via srun
                on a remote machine.

            References:
                https://stackoverflow.com/questions/56129786/cannot-load-backend-qt5agg-which-requires-the-qt5-interactive-framework-as
                https://github.com/ultralytics/ultralytics/issues/6939
            """
            try:
                # Note
                set_mpl_backend(self.prev)
            except ImportError as ex:
                if self.strict:
                    raise
                print(f'warning: kwplot.BackendContext was unable to switch back to: {self.prev} after switching to {self.backend}')
                if self._prev_backend_was_loaded:
                    # Just try to supress this if we cant switch back.
                    if "which requires the 'qt' interactive framework, as 'headless' is currently running" in str(ex):
                        ...
                    else:
                        raise
            except Exception:
                if self.strict:
                    raise
                if self._prev_backend_was_loaded:
                    # Only propogate the error if we had explicitly used pyplot
                    # beforehand. Note sure if this is the right thing to do.
                    raise
