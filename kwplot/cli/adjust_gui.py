"""
A rewrite an the utool preference GUI

References:
    ~/code/guitool_ibeis/guitool_ibeis/PrefWidget2.py
    ~/code/guitool_ibeis/guitool_ibeis/PreferenceWidget.py
    ~/code/utool/utool/Preferences.py
"""
import ubelt as ub
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from matplotlib.backend_bases import MouseEvent, KeyEvent, PickEvent
import matplotlib.backends.backend_qt5agg as backend_qt
from scriptconfig import smartcast as smartcast_mod


def report_thread_error(fn):
    """ Decorator to help catch errors that QT wont report """
    def report_thread_error_wrapper(*args, **kwargs):
        import traceback
        import sys
        try:
            ret = fn(*args, **kwargs)
            return ret
        except Exception as ex:
            print('\n\n *!!* Thread Raised Exception: ' + str(ex))
            print('\n\n *!!* Thread Exception Traceback: \n\n' + traceback.format_exc())
            sys.stdout.flush()
            et, ei, tb = sys.exc_info()
            raise
    return report_thread_error_wrapper


class _Indexer:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, key):
        return self.func(key)


class IndexedDict(dict):
    """
    Example:
        >>> from kwplot.cli.adjust_gui import *  # NOQA
        >>> self = IndexedDict({
        >>>     'a': 1,
        >>>     'b': 2,
        >>>     'c': 3,
        >>> })
        >>> self._index_to_key
        >>> self._key_to_index
        >>> self.iloc[2]
        >>> self.index[2]
    """

    def __init__(self, data=None, /, **kwargs):
        super().__init__()
        self._index_to_key = []
        self._key_to_index = {}
        if data is not None:
            assert not kwargs
            self.update(data)
        else:
            self.update(kwargs)

    def __delitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        if key not in self._key_to_index:
            index = len(self)
            super().__setitem__(key, value)
            self._key_to_index[key] = index
            self._index_to_key.append(key)
        else:
            super().__setitem__(key, value)

    def update(self, data):
        for key, value in data.items():
            self[key] = value

    @property
    def iloc(self):
        return _Indexer(self.value_atindex)

    def indexof(self, key):
        return self._key_to_index[key]

    @property
    def index(self):
        return self._index_to_key

    def key_atindex(self, index):
        key = self._index_to_key[index]
        return key

    def value_atindex(self, index):
        key = self._index_to_key[index]
        value = self[key]
        return value


class QConfigNode(ub.NiceRepr):
    """
    Backend data structure for a configuration tree
    """

    def __init__(self, value=ub.NoParam, parent=None):
        self.key = None
        self.parent = parent
        # Note: children and value should be mutually exclusive.
        # We should add another type param.
        self.value = value
        self.children = IndexedDict()

    def __nice__(self):
        if self.children:
            if self.value is None:
                return f'{ub.repr2(self.children, nl=1)}'
            else:
                return f'{self.value}, {ub.repr2(self.children, nl=1)}'
        else:
            return f'{self.value}'

    def add_child(self, key, child=None):
        if child is None:
            child = QConfigNode()
        child.parent = self
        child.key = key
        self.children[key] = child
        return child

    def qt_get_parent(self):
        return self.parent

    def qt_parents_index_of_me(self):
        if self.parent is None:
            return None
        else:
            return self.parent.children.indexof(self.key)

    def qt_get_child(self, row):
        return self.children.iloc[row]

    def qt_row_count(self):
        return len(self.children)

    def qt_col_count(self):
        return 2

    def qt_get_data(self, column):
        if column == 0:
            return self.key
        data = self.value
        if data is ub.NoParam:
            return ''
        elif data is None:
            # Check for a get of None
            data = 'None'
        return data

    def qt_type(self):
        return type(self.value)

    def qt_is_editable(self):
        return self.value is not ub.NoParam

    def qt_set_value(self, data):
        # TODO: casting
        data = smartcast_mod.smartcast(data)
        self.value = data

    def items(self):
        if self.value is not ub.NoParam:
            raise Exception('this is a leaf node')

        for key, child in self.children.items():
            if isinstance(child, QConfigNode):
                if child.value is ub.NoParam:
                    yield (key, dict(list(child.items())))
                else:
                    yield (key, child.value)
            else:
                raise TypeError

    def to_indexable(self):
        return dict(self.items())


class QConfigTree(QConfigNode):

    def _pathget(self, path):
        curr_ = self
        for p in path:
            curr_ = curr_.children[p]
        return curr_

    @classmethod
    def coerce(QConfigTree, data):
        if data is None:
            return QConfigTree()
        elif isinstance(data, QConfigTree):
            return data
        elif isinstance(data, dict):
            return QConfigTree.from_indexable(data)
        else:
            raise TypeError

    @classmethod
    def from_indexable(QConfigTree, config):
        """
        Create a tree from a nested dict

        Example:
            >>> from kwplot.cli.adjust_gui import *  # NOQA
            >>> config = {
            >>>     'algo1': {
            >>>         'opt1': 1,
            >>>         'opt2': 2,
            >>>     },
            >>>     'algo2': {
            >>>         'opt1': 1,
            >>>         'opt2': 2,
            >>>     },
            >>>     'general_opt': 'abc',
            >>> }
            >>> self = QConfigTree.from_indexable(config)
            >>> print('self = {}'.format(ub.urepr(self, nl=1)))
            >>> print(self.to_indexable())
        """
        self = QConfigTree()
        walker = ub.IndexableWalker(config)
        for path, value in walker:
            if isinstance(value, dict):
                *prefix, key = path
                parent = self._pathget(prefix)
                parent.add_child(key)
            else:
                *prefix, key = path
                parent = self._pathget(prefix)
                child = parent.add_child(key)
                child.value = value
        return self


class QConfigModel(QtCore.QAbstractItemModel):
    """
    Convention states only items with column index 0 can have children

    """
    @report_thread_error
    def __init__(self, root_config, parent=None):
        super(QConfigModel, self).__init__(parent)
        self.root_config = root_config

    @report_thread_error
    def index_to_node(self, index=QtCore.QModelIndex()):
        """ Internal helper method """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_config

    #-----------
    # Overloaded ItemModel Read Functions
    @report_thread_error
    def rowCount(self, parent=QtCore.QModelIndex()):
        parent_node = self.index_to_node(parent)
        return parent_node.qt_row_count()

    @report_thread_error
    def columnCount(self, parent=QtCore.QModelIndex()):
        parent_node = self.index_to_node(parent)
        return parent_node.qt_col_count()

    @report_thread_error
    def data(self, qtindex, role=Qt.DisplayRole):
        """
        Returns the data stored under the given role
        for the item referred to by the qtindex.
        """
        if not qtindex.isValid():
            return None
        # Specify CheckState Role:
        flags = self.flags(qtindex)
        if role == Qt.CheckStateRole:
            if flags & Qt.ItemIsUserCheckable:
                node = self.index_to_node(qtindex)
                data = node.qt_get_data(qtindex.column())
                return Qt.Checked if data else Qt.Unchecked
        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None
        node = self.index_to_node(qtindex)
        data = node.qt_get_data(qtindex.column())
        if isinstance(data, float):
            LOCALE = QtCore.QLocale()
            var = LOCALE.toString(float(data), format='g', precision=6)
        else:
            var = data
        return str(var)

    @report_thread_error
    def setData(self, qtindex, value, role=Qt.EditRole):
        """Sets the role data for the item at qtindex to value."""
        if role == Qt.EditRole:
            data = value
        elif role == Qt.CheckStateRole:
            data = (value == Qt.Checked)
        else:
            return False

        VERBOSE_PREF = 0
        if VERBOSE_PREF:
            print('[qt] --- setData() ---')
            print('[qt] role = %r' % role)
            print('[qt] value = %r' % value)
            print('[qt] type(data) = %r' % type(data))
            print('[qt] type(value) = %r' % type(value))

        node = self.index_to_node(qtindex)
        old_data = node.qt_get_data(qtindex.column())
        if VERBOSE_PREF:
            print('[qt] old_data = %r' % (old_data,))
            print('[qt] old_data != data = %r' % (old_data != data,))
        if old_data != data:
            node.qt_set_value(data)
        self.dataChanged.emit(qtindex, qtindex)
        return True

    @report_thread_error
    def index(self, row, col, parent=QtCore.QModelIndex()):
        """Returns the index of the item in the model specified
        by the given row, column and parent index."""
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()
        parent_node = self.index_to_node(parent)
        child_node = parent_node.children.iloc[row]
        if child_node:
            return self.createIndex(row, col, child_node)
        else:
            return QtCore.QModelIndex()

    @report_thread_error
    def parent(self, index=None):
        """Returns the parent of the model item with the given index.
        If the item has no parent, an invalid QModelIndex is returned."""
        if index is None:  # Overload with QtCore.QObject.parent()
            return QtCore.QObject.parent(self)
        if not index.isValid():
            return QtCore.QModelIndex()
        node = self.index_to_node(index)
        parent_node = node.qt_get_parent()
        if parent_node == self.root_config:
            return QtCore.QModelIndex()
        return self.createIndex(parent_node.qt_parents_index_of_me(), 0, parent_node)

    @report_thread_error
    def flags(self, index):
        """Returns the item flags for the given index."""
        if index.column() == 0:
            # The First Column is just a label and unchangable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if not index.isValid():
            return Qt.ItemFlag(0)
        child_node = self.index_to_node(index)
        if child_node:
            if child_node.qt_is_editable():
                if child_node.qt_type() is bool:
                    return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
                else:
                    return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemFlag(0)

    @report_thread_error
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return 'Key'
            if section == 1:
                return 'Value'
        return None


class QConfigWidget(QtWidgets.QWidget):

    data_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent, config=None):
        super().__init__(parent=parent)
        self.config_model = QConfigModel(config)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.prefTreeView = QtWidgets.QTreeView(self)
        self.prefTreeView.setObjectName('prefTreeView')

        self.prefTreeView.setModel(self.config_model)
        self.prefTreeView.header().resizeSection(0, 250)

        self.verticalLayout.addWidget(self.prefTreeView)

        self.prefTreeView.expandAll()

        self.config_model.dataChanged.connect(self._on_change)

    def _on_change(self, top_left, bottom_right):
        if top_left is bottom_right:
            # we know what index changed
            qtindex = top_left
            model = qtindex.model()
            # Find index with config key
            key_index = model.index(qtindex.row(), 0, qtindex.parent())
            key = key_index.data()
        else:
            key = None
        self.data_changed.emit(key)


class MatplotlibWidget(QtWidgets.QWidget):
    """
    A qt widget that contains a matplotlib figure

    References:
        http://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html
    """
    click_inside_signal = QtCore.pyqtSignal(MouseEvent, object)
    key_press_signal = QtCore.pyqtSignal(KeyEvent)
    pick_event_signal = QtCore.pyqtSignal(PickEvent)

    def __init__(self, *args, **kwargs):
        # from plottool_ibeis.interactions import zoom_factory, pan_factory
        # from plottool_ibeis import abstract_interaction
        super().__init__(*args, **kwargs)
        from matplotlib.figure import Figure
        # Create unmanaged figure and a canvas
        self.fig = Figure()
        self.fig._no_raise_plottool_ibeis = True
        self.canvas = backend_qt.FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.canvas)

        # Workaround key_press bug
        # References: https://github.com/matplotlib/matplotlib/issues/707
        self.canvas.setFocusPolicy(Qt.ClickFocus)

        self.reset_ax()

        # self.ax = self.fig.add_subplot(1, 1, 1)
        # pt.adjust_subplots(left=0, right=1, top=1, bottom=0, fig=self.fig)
        # if pan_and_zoom or True:
        #     self.pan_events = pan_factory(self.ax)
        #     self.zoon_events = zoom_factory(self.ax)

        self.fig.canvas.mpl_connect('button_press_event', self._emit_button_press)
        self.fig.canvas.mpl_connect('key_press_event', self.key_press_signal.emit)
        self.fig.canvas.mpl_connect('pick_event', self.pick_event_signal.emit)

        # self.MOUSE_BUTTONS = abstract_interaction.AbstractInteraction.MOUSE_BUTTONS
        self.setMinimumHeight(20)
        self.setMinimumWidth(20)

        self.installEventFilter(self.parent())

    def clf(self):
        self.fig.clf()
        self.reset_ax()

    def reset_ax(self):
        # from plottool_ibeis.interactions import zoom_factory, pan_factory
        self.ax = self.fig.add_subplot(1, 1, 1)
        # pt.adjust_subplots(left=0, right=1, top=1, bottom=0, fig=self.fig)
        # self.pan_events = pan_factory(self.ax)
        # self.zoon_events = zoom_factory(self.ax)
        return self.ax

    def _emit_button_press(self, event):
        from plottool_ibeis import interact_helpers as ih
        if ih.clicked_inside_axis(event):
            self.click_inside_signal.emit(event, event.inaxes)


class AdjustWidget(QtWidgets.QWidget):

    def __init__(self, config=None, raw_img=None):
        super().__init__()
        self.raw_img = raw_img
        self.config = QConfigTree.coerce(config)
        layout = QtWidgets.QVBoxLayout(self)
        self.config_widget = QConfigWidget(self, self.config)
        self.setLayout(layout)
        self.mpl_widget = MatplotlibWidget(parent=self)
        layout.addWidget(self.mpl_widget)
        layout.addWidget(self.config_widget)
        self.config_widget.data_changed.connect(self.update_normalization)
        self.update_normalization()

    def update_normalization(self, key=None):
        import kwimage
        config_dict = self.config.to_indexable()
        params = config_dict['params']
        print('Update Norm')
        print('params = {}'.format(ub.urepr(params, nl=1)))
        self.norm_img = kwimage.normalize_intensity(self.raw_img, params=params)
        print(self.norm_img.sum())
        self.mpl_widget.fig.gca().imshow(self.norm_img)
        self.mpl_widget.fig.canvas.draw()


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('GTK+')

    import kwimage
    raw_img = kwimage.grab_test_image()

    # fpath =

    config = {
        'params': {
            'scaling': 'sigmoid',
            'extrema': 'custom-quantile',
            'low': 0.1,
            'center': 0.8,
            'high': 0.9,
        },
    }

    widget = AdjustWidget(config, raw_img)
    widget.show()
    widget.resize(int(800), 600)

    # %gui qt

    # import IPython.lib.guisupport
    # IPython.lib.guisupport.start_event_loop_qt5(app)
    retcode = app.exec_()
    print('QAPP retcode = %r' % (retcode,))
    app.exit(retcode)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/kwplot/kwplot/cli/adjust_gui.py
    """
    main()
