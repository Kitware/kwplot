#!/usr/bin/env python3
"""
A rewrite an the utool preference GUI

References:
    ~/code/guitool_ibeis/guitool_ibeis/PrefWidget2.py
    ~/code/guitool_ibeis/guitool_ibeis/PreferenceWidget.py
    ~/code/utool/utool/Preferences.py
"""
import ubelt as ub
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from matplotlib.backend_bases import MouseEvent, KeyEvent, PickEvent
import matplotlib.backends.backend_qt5agg as backend_qt
from scriptconfig import smartcast as smartcast_mod
from enum import Enum
import scriptconfig as scfg


class AdjustGuiConfig(scfg.DataConfig):
    img_fpath = scfg.Value(None, help='input', position=1)


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


try:
    NoValue  # pragma: no cover
except NameError:  # pragma: no cover
    NoValue = object.__new__(ub.util_const.NoParamType)  # type: NoParamType


class _Qt_ConfigNodeMixin:
    """
    Extension of the config node with method specifically for Qt data models
    """

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
        if data is NoValue:
            return ''
        elif data is None:
            # Check for a get of None
            data = 'None'
        return data

    def qt_type(self):
        return type(self.value)

    def qt_is_editable(self):
        return self.value is not NoValue

    def qt_set_value(self, data):
        # TODO: casting
        data = smartcast_mod.smartcast(data)
        self.value = data

    def qt_delegate_style(self):
        return self.delegate_style


class QConfigNode(ub.NiceRepr, _Qt_ConfigNodeMixin):
    """
    Backend data structure for a configuration tree

    Note:
        The value of children may be dependent on the value.

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
        >>> self = ConfigNode.from_indexable(config)
        >>> print('self = {}'.format(ub.urepr(self, nl=1)))
        >>> print(self.to_indexable())
    """

    def __init__(self, value=NoValue, type=None, parent=None, choices=None,
                 min_value=None, max_value=None, step_value=None,
                 nullable=True, help=None):
        self.parent = parent
        self.key = None
        self.type = type
        self.value = value
        self.children = IndexedDict()

        if choices is not None:
            self.delegate_style = DelegateStyle.COMBO_BOX
        elif min_value is not None or max_value is not None or step_value is not None:
            self.delegate_style = DelegateStyle.SPINNER
        else:
            self.delegate_style = None

        ### TODO: not sure if these belong here or in some subclass or
        ### other construct
        self.nullable = nullable
        self.choices = choices
        self.min_value = min_value
        self.max_value = max_value
        self.step_value = step_value

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

    def items(self):
        if self.value is not NoValue:
            raise Exception('this is a leaf node')

        for key, child in self.children.items():
            if isinstance(child, QConfigNode):
                if child.value is NoValue:
                    yield (key, dict(list(child.items())))
                else:
                    yield (key, child.value)
            else:
                raise TypeError

    def to_indexable(self):
        return dict(self.items())

    def _pathget(self, path):
        curr_ = self
        for p in path:
            curr_ = curr_.children[p]
        return curr_

    @classmethod
    def coerce(cls, data):
        if data is None:
            return cls()
        elif isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls.from_indexable(data)
        else:
            raise TypeError

    @classmethod
    def from_indexable(cls, config):
        """
        Create a tree from a nested dict
        """
        self = cls()
        walker = ub.IndexableWalker(config)
        for path, value in walker:
            if isinstance(value, dict):
                *prefix, key = path
                parent = self._pathget(prefix)
                parent.add_child(key)
            elif isinstance(value, cls):
                *prefix, key = path
                parent = self._pathget(prefix)
                parent.add_child(key, child=value)
            else:
                # Leaf
                *prefix, key = path
                parent = self._pathget(prefix)
                child = parent.add_child(key)
                child.value = value
        return self


class CustomComboBox(QtWidgets.QComboBox):
    def __init__(combo, parent=None, default=None, options=None, changed=None):
        super().__init__(parent=parent)
        options = [opt if isinstance(opt, tuple) and len(opt) == 2 else
                   (str(opt), opt) for opt in options]
        combo.options = options
        combo.changed = changed
        combo.updateOptions()
        combo.setDefault(default)
        combo.currentIndexChanged['int'].connect(combo.currentIndexChangedCustom)

    def currentValue(combo):
        index = combo.currentIndex()
        opt = combo.options[index]
        value = opt[1]
        return value

    def setOptions(combo, options):
        flags = [isinstance(opt, tuple) and len(opt) == 2 for opt in options]
        options = [opt if flag else (str(opt), opt)
                    for flag, opt in zip(flags, options)]
        combo.options = options

    def updateOptions(combo, reselect=False, reselect_index=None):
        if reselect_index is None:
            reselect_index = combo.currentIndex()
        combo.clear()
        combo.addItems( [ option[0] for option in combo.options ] )
        if reselect and reselect_index < len(combo.options):
            combo.setCurrentIndex(reselect_index)

    def setOptionText(combo, option_text_list):
        for index, text in enumerate(option_text_list):
            combo.setItemText(index, text)

    def currentIndexChangedCustom(combo, index):
        if combo.changed is not None:
            combo.changed(index, combo.options[index][1])

    def setDefault(combo, default=None):
        if default is not None:
            combo.setCurrentValue(default)
        else:
            combo.setCurrentIndex(0)

    def setCurrentValue(combo, value):
        index = combo.findValueIndex(value)
        combo.setCurrentIndex(index)

    def findValueIndex(combo, value):
        """ finds index of backend value and sets the current index """
        for index, (text, val) in enumerate(combo.options):
            if value == val:
                return index
        else:
            # Hack, try the text if value doesnt work
            for index, (text, val) in enumerate(combo.options):
                if value == text:
                    return index
            else:
                raise ValueError('No such option value=%r' % (value,))


class NullableSpinBox(QtWidgets.QDoubleSpinBox):
    """
    Custom spin box that handles None / nan values
    """
    _EXP = 29
    HARD_MIN = float(-2 ** _EXP) - 1.0
    HARD_MAX = float(2 ** _EXP) + 1.0
    NONE_VALUE = HARD_MIN + 1.0

    def __init__(self, *args, **kwargs):
        self.type = kwargs.pop('type', float)
        self.nullable = kwargs.pop('nullable', True)
        self.post_nan_value = 0
        self._hack_min = self.HARD_MIN + 2.0
        self._hack_max = self.HARD_MAX - 2.0
        super().__init__(*args, **kwargs)
        super().setRange(self.HARD_MIN, self.HARD_MAX)

    def keyPressEvent(self, event):
        if self.nullable and event.matches(QtGui.QKeySequence.Delete):
            self.setValue(self.NONE_VALUE)
        else:
            return super().keyPressEvent(event)

    def setMinimum(self, min_value):
        """ hack to get around None being invalid """
        self._hack_min = min_value

    def setMaximum(self, max_value):
        self._hack_max = max_value

    def setRange(self, min_value, max_value):
        self._hack_min = min_value
        self._hack_max = max_value

    def stepBy(self, steps):
        current_value = self.value()
        if current_value is None:
            self.setValue(self.post_nan_value)
        else:
            self.setValue(current_value + steps * self.singleStep())

    def validate(self, text, pos):
        import re
        if self.nullable and (len(text) == 0 or text.lower().startswith('n')):
            state = (QtGui.QValidator.Acceptable, text, pos)
        else:
            if self._hack_min >= 0 and text.startswith('-'):
                state = (QtGui.QValidator.Invalid, text, pos)
            else:
                if not re.match(r'^[+-]?[0-9]*[.,]?[0-9]*[Ee]?[+-]?[0-9]*$', text, flags=re.MULTILINE):
                    state = (QtGui.QValidator.Invalid, text, pos)
                else:
                    try:
                        val = float(text)
                        if val >= self._hack_min and val <= self._hack_max:
                            state = (QtGui.QValidator.Acceptable, text, pos)
                        else:
                            state = (QtGui.QValidator.Invalid, text, pos)
                    except Exception:
                        state = (QtGui.QValidator.Intermediate, text, pos)
        return state

    def value(self):
        internal_value = super().value()
        if self.nullable and internal_value == self.NONE_VALUE:
            return None
        else:
            return internal_value

    def setValue(self, value):
        if value is None:
            value = self.NONE_VALUE
        if isinstance(value, str):
            value = self.valueFromText(value)
        if value != self.NONE_VALUE:
            value = max(value, self._hack_min)
            value = min(value, self._hack_max)
        return super().setValue(value)

    def valueFromText(self, text):
        if self.nullable and (len(text) == 0 or text[0:1].lower().startswith('n')):
            value = self.NONE_VALUE
        else:
            if self.type is int:
                value = int(round(float(text)))
            elif self.type is float:
                value = self.type(text)
            else:
                # raise ValueError('unknown self.type=%r' % (self.type,))
                value = float(text)
        return value

    def textFromValue(self, value):
        if self.nullable and value is None or value == self.NONE_VALUE:
            text = 'None'
        else:
            if self.type is int:
                text = str(int(value))
            elif self.type is float:
                text = str(float(value))
            else:
                text = str(value)
                # raise ValueError('unknown self.type=%r' % (self.type,))
        return text


class DelegateStyle(Enum):
    NONE = 0
    COMBO_BOX = 1
    SPINNER = 2


class ConfigValueDelegate(QtWidgets.QStyledItemDelegate):
    """
    A delegate that decides what the editor should be for each row in a
    specific column

    References:
        http://stackoverflow.com/questions/28037126/how-to-use-qcombobox-as-delegate-with-qtableview
        http://www.qtcentre.org/threads/41409-PyQt-QTableView-with-comboBox
        http://stackoverflow.com/questions/28680150/qtableview-data-in-background--cell-is-edited
        https://forum.qt.io/topic/46628/qtreeview-with-qitemdelegate-and-qcombobox-inside-not-work-propertly/5
        http://stackoverflow.com/questions/33990029/what-are-the-mechanics-of-the-default-delegate-for-item-views-in-qt
        http://www.qtcentre.org/archive/index.php/t-64165.html
        http://doc.qt.io/qt-4.8/style-reference.html

    """
    def paint(self, painter, option, index):
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            curent_value = str(index.model().data(index))
            style = QtWidgets.QApplication.style()
            opt = QtWidgets.QStyleOptionComboBox()

            opt.currentText = curent_value
            opt.rect = option.rect
            opt.editable = False
            opt.frame = True

            if leaf_node.qt_is_editable():
                opt.state |= style.State_On
                opt.state |= style.State_Enabled
                opt.state = style.State_Enabled | style.State_Active

            element = QtWidgets.QStyle.CE_ComboBoxLabel
            control = QtWidgets.QStyle.CC_ComboBox

            style.drawComplexControl(control, opt, painter)
            style.drawControl(element, opt, painter)
        else:
            return super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        """
        Creates different editors for different types of data
        """
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            options = leaf_node.choices
            curent_value = index.model().data(index)
            editor = CustomComboBox(parent=parent, options=options,
                                    default=curent_value)
            editor.currentIndexChanged['int'].connect(self.currentIndexChanged)
            editor.setAutoFillBackground(True)
        elif delegate_style == DelegateStyle.SPINNER:
            editor = NullableSpinBox(parent, type=leaf_node.type, nullable=leaf_node.nullable)

            if leaf_node.min_value is not None:
                editor.setMinimum(leaf_node.min_value)
            if leaf_node.max_value is not None:
                editor.setMaximum(leaf_node.max_value)

            step_value = leaf_node.step_value
            if step_value is None:
                # Autoset the step value
                if leaf_node.min_value is not None and leaf_node.max_value is not None:
                    step_value = (leaf_node.max_value - leaf_node.min_value) / 20

            if step_value is not None:
                editor.setSingleStep(step_value)

            editor.setAutoFillBackground(True)
            editor.setHidden(False)
            curent_value = index.model().data(index)
            editor.setValue(curent_value)
        else:
            editor = super().createEditor(parent, option, index)
            editor.setAutoFillBackground(True)
            # editor.keyPressEvent
        return editor

    def setEditorData(self, editor, index):
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            editor.blockSignals(True)
            current_data = index.model().data(index)
            editor.setCurrentValue(current_data)
            editor.blockSignals(False)
        else:
            return super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            current_value = editor.currentValue()
            model.setData(index, current_value)
        elif delegate_style == DelegateStyle.SPINNER:
            current_value = editor.value()
            model.setData(index, current_value)
        else:
            return super().setModelData(editor, model, index)

    def currentIndexChanged(self, combo_idx):
        sender = self.sender()
        self.commitData.emit(sender)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def editorEvent(self, event, model, option, index):
        return super().editorEvent(event, model, option, index)

    def eventFilter(self, editor, event):
        handled =  super().eventFilter(editor, event)
        return handled


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
        node = self.index_to_node(qtindex)
        old_data = node.qt_get_data(qtindex.column())
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

        self.vert_layout = QtWidgets.QVBoxLayout(self)
        self.tree_view = QtWidgets.QTreeView(self)
        self.tree_view.setObjectName('tree_view')

        self.delegate = ConfigValueDelegate(self.tree_view)
        self.tree_view.setItemDelegateForColumn(1, self.delegate)

        self.tree_view.setModel(self.config_model)
        self.tree_view.header().resizeSection(0, 250)

        self.vert_layout.addWidget(self.tree_view)

        self.tree_view.expandAll()

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
        in_axis = event is not None and (event.inaxes is not None and event.xdata is not None)
        if in_axis:
            self.click_inside_signal.emit(event, event.inaxes)


class AdjustWidget(QtWidgets.QWidget):

    def __init__(self, config=None, raw_img=None):
        super().__init__()
        self.raw_img = raw_img
        self.config = QConfigNode.coerce(config)
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

    def _devcheck(self, raw_img):
        import kwplot
        kwplot.autompl()
        sns = kwplot.autosns()

        fig = kwplot.figure(fnum=1)
        fig.clf()
        ax1 = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)
        ax1.imshow(raw_img)
        ax1.grid(False)
        ax2

        import numpy as np
        counts, bins = np.histogram(raw_img, bins=256)
        centers = (bins[1:] + bins[0:-1]) / 2
        from watch.cli.coco_spectra import _weighted_auto_bins
        import pandas as pd
        data = pd.DataFrame({'value': centers, 'weight': counts})
        n_equal_bins = _weighted_auto_bins(data, 'value', 'weight')

        hist_data_kw = dict(
            x='value',
            weights='weight',
            bins=n_equal_bins,
            # bins=config['bins'],
            # stat=config['stat'],
            # hue='channel',
        )
        hist_style_kw = dict(
            # palette=palette,
            # fill=config['fill'],
            # element=config['element'],
            # multiple=config['multiple'],
            # kde=config['kde'],
            # cumulative=config['cumulative'],
        )

        hist_data_kw_ = hist_data_kw.copy()
        # if hist_data_kw_['bins'] == 'auto':
        #     xvar = hist_data_kw['x']
        #     weightvar = hist_data_kw['weights']
        #     hist_data_kw_['bins'] = _weighted_auto_bins(sensor_df, xvar, weightvar)
        sns.histplot(ax=ax2, data=data, **hist_data_kw_, **hist_style_kw)


def main(cmdline=1, **kwargs):
    config = AdjustGuiConfig.cli(cmdline=cmdline, data=kwargs, strict=True)
    print('config = ' + ub.urepr(dict(config), nl=1))

    import sys
    import kwimage
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('GTK+')

    if config.img_fpath is not None:
        raw_img = kwimage.imread(config.img_fpath)
    else:
        raw_img = kwimage.grab_test_image()

    config = {
        'params': {
            'scaling': QConfigNode('sigmoid', choices=['sigmoid', 'linear']),
            'extrema': QConfigNode('custom-quantile', choices=['quantile', 'adaptive-quantile', 'iqr', 'iqr-clip']),
            'low': QConfigNode(0.1, min_value=0.0, max_value=1.0, step_value=0.05),
            'mid': QConfigNode(0.5, min_value=0.0, max_value=1.0, step_value=0.05),
            'high': QConfigNode(0.9, min_value=0.0, max_value=1.0, step_value=0.05),
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
        python -m kwplot.cli.adjust_gui
    """
    main()
