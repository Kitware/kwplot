#!/usr/bin/env python3
"""
A rewrite an the utool preference GUI

Notes:
    This needs to be cleaned up, the QT widget components should be separate
    from the Qt-aware configurable stuff.

References:
    ~/code/guitool_ibeis/guitool_ibeis/PrefWidget2.py
    ~/code/guitool_ibeis/guitool_ibeis/PreferenceWidget.py
    ~/code/utool/utool/Preferences.py
"""
from __future__ import annotations

from typing import (
    Any, Callable, Dict, Generator, Optional, Sequence, Tuple, Type,
    TypeVar, Union, cast,
)

import ubelt as ub
from PyQt5 import QtWidgets  # type: ignore
from PyQt5 import QtCore  # type: ignore
from PyQt5 import QtGui  # type: ignore
from PyQt5.QtCore import Qt  # type: ignore
from matplotlib.backend_bases import MouseEvent, KeyEvent, PickEvent
import matplotlib.backends.backend_qt5agg as backend_qt
from scriptconfig import smartcast as smartcast_mod
from enum import Enum
import scriptconfig as scfg


_Qt = cast(Any, Qt)
_QValidator = cast(Any, QtGui.QValidator)
_QStyle = cast(Any, QtWidgets.QStyle)


class AdjustGuiConfig(scfg.DataConfig):
    """
    Helper to find good robust normalization parameters for input images.

    This tool allows cropping and normalization of input images using robust
    statistics. It is useful for tuning contrast and visualization parameters
    interactively or programmatically.
    """

    img_fpath = scfg.Value(None, help='Path to the input image file.', position=1)

    scaling = scfg.Value(
        'sigmoid', choices=['sigmoid', 'linear'],
        help=ub.codeblock(
            '''
            Scaling function used for normalization:
            - 'sigmoid': nonlinear sigmoid mapping centered at `mid`
            - 'linear' : linear rescaling between `low` and `high`
            '''
        ))

    extrema = scfg.Value(
        'quantile', choices=['quantile', 'adaptive-quantile', 'iqr',
                             'iqr-clip'],
        help=ub.codeblock(
            '''
            Method used to estimate low/mid/high intensity thresholds:
            - 'quantile'         : empirical percentiles
            - 'adaptive-quantile': quantile with local adaptation
            - 'iqr'              : interquartile range
            - 'iqr-clip'         : IQR with clipping of outliers
            '''
        ))

    low = scfg.Value(0.1, help='Lower bound percentile or IQR quantile (range: 0.0–1.0).')

    mid = scfg.Value(0.5, help='Midpoint intensity (used in sigmoid scaling, range: 0.0–1.0).')

    high = scfg.Value(0.9, help='Upper bound percentile or IQR quantile (range: 0.0–1.0).')

    crop = scfg.Value("null", type=str, help=ub.codeblock(
        '''
        Optional crop string in the form "y1:y2,x1:x2".

        Use empty values for open-ended slices, e.g.:
        "10:, :100" → rows from 10 to end, columns from start to 100

        Set to "null" to disable cropping.
        '''))

    expr = scfg.Value("null", type=str, help=ub.codeblock(
        '''
        Optional Python expression to transform the image after cropping.

        This is evaluated as `eval(expr)` with `img` bound to the cropped
        image (i.e., `img = self.processed_img`).

        Example:
        "np.log1p(img)"
        "img[::2, ::2]"

        Set to "null" to disable expression evaluation.
        '''
    ))

    cmap = scfg.Value(
        'None', type=str, help=ub.codeblock(
            '''
            Optional matplotlib colormap to apply when displaying the image.

            Examples:
            "gray", "viridis", "magma"

            Set to "None" or "null" to use default colormap behavior.
            '''
        ))


_F = TypeVar('_F', bound=Callable[..., Any])


def report_thread_error(fn: _F) -> _F:
    """ Decorator to help catch errors that QT wont report """
    def report_thread_error_wrapper(*args: Any, **kwargs: Any) -> Any:
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
    typed_wrapper = cast(_F, report_thread_error_wrapper)
    return typed_wrapper


class _Indexer:
    def __init__(self, func: Callable[[Any], Any]) -> None:
        self.func = func

    def __getitem__(self, key: Any) -> Any:
        return self.func(key)


class IndexedDict(dict):
    """
    Example:
        >>> # xdoctest: +SKIP
        >>> # xdoctest: +REQUIRES(module:PyQt5)
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

    # def __init__(self, data=None, /, **kwargs):  # python 3.8+
    def __init__(self, data: Any = None, **kwargs: Any) -> None:
        super().__init__()
        self._index_to_key = []
        self._key_to_index = {}
        if data is not None:
            assert not kwargs
            self.update(data)
        else:
            self.update(kwargs)

    def __delitem__(self, key: Any) -> None:
        raise NotImplementedError

    def __setitem__(self, key: Any, value: Any) -> None:
        if key not in self._key_to_index:
            index = len(self)
            super().__setitem__(key, value)
            self._key_to_index[key] = index
            self._index_to_key.append(key)
        else:
            super().__setitem__(key, value)

    def update(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1:
            data = args[0]
        else:
            assert len(args) == 0
            data = None
        if data is not None:
            for key, value in data.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    @property
    def iloc(self) -> _Indexer:
        return _Indexer(self.value_atindex)

    def indexof(self, key: Any) -> int:
        return self._key_to_index[key]

    @property
    def index(self) -> list:
        return self._index_to_key

    def key_atindex(self, index: int) -> Any:
        key = self._index_to_key[index]
        return key

    def value_atindex(self, index: int) -> Any:
        key = self._index_to_key[index]
        value = self[key]
        return value

NoValue: Any = object.__new__(ub.util_const.NoParamType)


class _Qt_ConfigNodeMixin:
    """
    Extension of the config node with method specifically for Qt data models
    """

    parent: Optional[Any]
    key: Any
    value: Any
    children: IndexedDict
    delegate_style: Optional[Any]
    _qt_observer_id_to_persistent_index: Dict[int, Any]
    _qt_observer_id_to_observers: Dict[int, Any]

    def qt_get_parent(self) -> Optional[QConfigNode]:
        return self.parent

    def qt_parents_index_of_me(self) -> Optional[int]:
        if self.parent is None:
            return None
        else:
            return self.parent.children.indexof(self.key)

    def qt_get_child(self, row: int) -> QConfigNode:
        return self.children.iloc[row]

    def qt_row_count(self) -> int:
        return len(self.children)

    def qt_col_count(self) -> int:
        return 2

    def qt_get_data(self, column: int) -> Any:
        if column == 0:
            return self.key
        data = self.value
        if data is NoValue:
            return ''
        elif data is None:
            # Check for a get of None
            data = 'None'
        return data

    def qt_type(self) -> Type[Any]:
        return type(self.value)

    def qt_is_editable(self) -> bool:
        return self.value is not NoValue

    def qt_set_value(self, data: Any) -> None:
        # TODO: casting
        data = smartcast_mod.smartcast(data, allow_split=False)
        self.value = data

    def qt_delegate_style(self) -> Optional[DelegateStyle]:
        return self.delegate_style

    def qt_set_persistant_index(self, index: Any, observer: Any) -> None:
        """Remember a persistent model index for a particular observer."""
        observer_id = id(observer)
        self._qt_observer_id_to_observers[observer_id] = observer
        self._qt_observer_id_to_persistent_index[observer_id] = index

    def qt_get_persistant_index(self, observer: Any) -> Any:
        """Look up the persistent model index for an observer."""
        observer_id = id(observer)
        return self._qt_observer_id_to_persistent_index[observer_id]

    def qt_observers(self) -> Generator[Any, None, None]:
        yield from self._qt_observer_id_to_observers.values()


class QConfigNode(ub.NiceRepr, _Qt_ConfigNodeMixin):
    """
    Backend data structure for a configuration tree

    Note:
        The value of children may be dependent on the value.

    Example:
        >>> # xdoctest: +SKIP
        >>> # xdoctest: +REQUIRES(module:PyQt5)
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
        >>>     'general_opt1': 'abc',
        >>>     'general_opt2': 'abc,efg',
        >>> }
        >>> self = QConfigNode.from_indexable(config)
        >>> print('self = {}'.format(ub.urepr(self, nl=1)))
        >>> config = self.to_indexable()
        >>> print(f'config = {ub.urepr(config, nl=1)}')
        >>> self.children['general_opt2'].qt_set_value('fds,fds')
        >>> assert self.children['general_opt2'].value == 'fds,fds'
        >>> config = self.to_indexable()
        >>> print(f'config = {ub.urepr(config, nl=1)}')
        >>> assert config['general_opt2'] == 'fds,fds'
    """

    def __init__(
            self, value: Any = NoValue, type: Optional[Type[Any]] = None,
            parent: Optional[QConfigNode] = None, choices: Any = None,
            min_value: Optional[float] = None, max_value: Optional[float] = None,
            step_value: Optional[float] = None, nullable: bool = True,
            help: Optional[str] = None,
    ) -> None:
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

        self._qt_observer_id_to_persistent_index = {}
        self._qt_observer_id_to_observers = {}

    def __nice__(self) -> str:
        if self.children:
            if self.value is None:
                return f'{ub.urepr(self.children, nl=1)}'
            else:
                return f'{self.value}, {ub.urepr(self.children, nl=1)}'
        else:
            return f'{self.value}'

    def add_child(self, key: Any, child: Optional[QConfigNode] = None) -> QConfigNode:
        if child is None:
            child = QConfigNode()
        child.parent = self
        child.key = key
        self.children[key] = child
        return child

    def items(self) -> Generator[Tuple[Any, Any], None, None]:
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

    def to_indexable(self) -> Dict[Any, Any]:
        return dict(self.items())

    def _pathget(self, path: Sequence[Any]) -> QConfigNode:
        curr_ = self
        for p in path:
            curr_ = curr_.children[p]
        return curr_

    @classmethod
    def coerce(cls, data: Any) -> QConfigNode:
        if data is None:
            return cls()
        elif isinstance(data, cls):
            return data
        elif isinstance(data, dict):
            return cls.from_indexable(data)
        else:
            raise TypeError

    @classmethod
    def from_indexable(cls, config: Dict[Any, Any]) -> QConfigNode:
        """
        Create a tree from a nested dict
        """
        self = cls()
        walker = ub.IndexableWalker(config)
        walker_iter = cast(Any, walker)
        for path, value in walker_iter:
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
    def __init__(
            combo, parent: Any = None, default: Any = None,
            options: Any = None, changed: Any = None,
    ) -> None:
        super().__init__(parent=parent)
        options = [opt if isinstance(opt, tuple) and len(opt) == 2 else
                   (str(opt), opt) for opt in options]
        combo.options = options
        combo.changed = changed
        combo.updateOptions()
        combo.setDefault(default)
        combo.currentIndexChanged['int'].connect(combo.currentIndexChangedCustom)

    def currentValue(combo) -> Any:
        index = combo.currentIndex()
        opt = combo.options[index]
        value = opt[1]
        return value

    def setOptions(combo, options: Sequence[Any]) -> None:
        flags = [isinstance(opt, tuple) and len(opt) == 2 for opt in options]
        options = [opt if flag else (str(opt), opt)
                    for flag, opt in zip(flags, options)]
        combo.options = options

    def updateOptions(combo, reselect: bool = False, reselect_index: Optional[int] = None) -> None:
        if reselect_index is None:
            reselect_index = combo.currentIndex()
        combo.clear()
        combo.addItems( [ option[0] for option in combo.options ] )
        if reselect and reselect_index < len(combo.options):
            combo.setCurrentIndex(reselect_index)

    def setOptionText(combo, option_text_list: Sequence[str]) -> None:
        for index, text in enumerate(option_text_list):
            combo.setItemText(index, text)

    def currentIndexChangedCustom(combo, index: int) -> None:
        if combo.changed is not None:
            combo.changed(index, combo.options[index][1])

    def setDefault(combo, default: Any = None) -> None:
        if default is not None:
            combo.setCurrentValue(default)
        else:
            combo.setCurrentIndex(0)

    def setCurrentValue(combo, value: Any) -> None:
        index = combo.findValueIndex(value)
        combo.setCurrentIndex(index)

    def findValueIndex(combo, value: Any) -> int:
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.type = kwargs.pop('type', float)
        self.nullable = kwargs.pop('nullable', True)
        self.post_nan_value = 0
        self._hack_min = self.HARD_MIN + 2.0
        self._hack_max = self.HARD_MAX - 2.0
        super().__init__(*args, **kwargs)
        super().setRange(self.HARD_MIN, self.HARD_MAX)

    def keyPressEvent(self, e: Optional[QtGui.QKeyEvent]) -> None:
        if self.nullable and e is not None and e.matches(QtGui.QKeySequence.Delete):
            self.setValue(self.NONE_VALUE)
        else:
            super().keyPressEvent(e)

    def setMinimum(self, min: float) -> None:
        """Hack to get around None being invalid."""
        self._hack_min = min

    def setMaximum(self, max: float) -> None:
        self._hack_max = max

    def setRange(self, min: float, max: float) -> None:
        self._hack_min = min
        self._hack_max = max

    def stepBy(self, steps: int) -> None:
        current_value = self.value()
        if current_value is None:
            self.setValue(self.post_nan_value)
        else:
            self.setValue(current_value + steps * self.singleStep())

    def validate(self, input: Optional[str], pos: int) -> Tuple[Any, str, int]:
        import re
        text = '' if input is None else input
        if self.nullable and (len(text) == 0 or text.lower().startswith('n')):
            state = (_QValidator.Acceptable, text, pos)
        else:
            if self._hack_min >= 0 and text.startswith('-'):
                state = (_QValidator.Invalid, text, pos)
            else:
                if not re.match(r'^[+-]?[0-9]*[.,]?[0-9]*[Ee]?[+-]?[0-9]*$', text, flags=re.MULTILINE):
                    state = (_QValidator.Invalid, text, pos)
                else:
                    try:
                        val = float(text)
                        if val >= self._hack_min and val <= self._hack_max:
                            state = (_QValidator.Acceptable, text, pos)
                        else:
                            state = (_QValidator.Invalid, text, pos)
                    except Exception:
                        state = (_QValidator.Intermediate, text, pos)
        return state

    def value(self) -> Optional[float]:  # type: ignore
        internal_value = super().value()
        if self.nullable and internal_value == self.NONE_VALUE:
            return None
        else:
            return internal_value

    def setValue(self, val: Optional[Union[float, str]]) -> None:
        value: Union[float, str] = self.NONE_VALUE if val is None else val
        if isinstance(value, str):
            value = self.valueFromText(value)
        if value != self.NONE_VALUE:
            value = max(value, self._hack_min)
            value = min(value, self._hack_max)
        super().setValue(float(value))

    def valueFromText(self, text: Optional[str]) -> float:
        text = '' if text is None else text
        if self.nullable and (len(text) == 0 or text[0:1].lower().startswith('n')):
            value = self.NONE_VALUE
        else:
            if self.type is int:
                value = int(round(float(text)))
            elif self.type is float:
                value = self.type(text)
            else:
                value = float(text)
        return float(value)

    def textFromValue(self, v: float) -> str:
        value = v
        if self.nullable and value == self.NONE_VALUE:
            text = 'None'
        else:
            if self.type is int:
                text = str(int(value))
            elif self.type is float:
                text = str(float(value))
            else:
                text = str(value)
        return text


class QConfigModel(QtCore.QAbstractItemModel):
    """
    The abstract data model that interfaces between the QConfigNode backend
    data structure and some frontend QTreeView used to interact with the data
    in a QWidget.

    Note:
        Convention states only items with column index 0 can have children

    Example:
        >>> # xdoctest: +SKIP
        >>> # xdoctest: +REQUIRES(module:PyQt5)
        >>> from kwplot.cli.adjust_gui import *  # NOQA
        >>> config = {
        >>>     'algo1': {
        >>>         'opt1': 1,
        >>>         'opt2': 2,
        >>>     },
        >>>     'algo2': {
        >>>         'opt1': 11,
        >>>         'opt2': 22,
        >>>     },
        >>>     'general_opt': 'abc',
        >>> }
        >>> root_config = QConfigNode.from_indexable(config)
        >>> self = QConfigModel(root_config)
        >>> index1 = self.parent()
        >>> index2 = self.index(0, 0)
        >>> algo1 = index2.internalPointer()
        >>> assert algo1 == root_config.children['algo1']
        >>> opt1 = self.index(0, 1, parent=index2).internalPointer()
        >>> assert opt1.key == 'opt1'
        >>> pindex = root_config.children['algo1'].qt_get_persistant_index(self)
        >>> index = QtCore.QModelIndex(pindex)
        >>> self.setData(index, 'foo')
        >>> got_value = self.data(index)  # why does this not return foo?
        >>> config = self.root_config.to_indexable()
        >>> print(f'config = {ub.urepr(config, nl=1)}')
        >>> assert config['algo1'] == 'foo'
        >>> self.setData(index, 'foo,bar')
        >>> config = self.root_config.to_indexable()
        >>> print(f'config = {ub.urepr(config, nl=1)}')
        >>> assert config['algo1'] == 'foo,bar'
    """
    @report_thread_error
    def __init__(self, root_config: Any, parent: Any = None) -> None:
        super(QConfigModel, self).__init__(parent)
        self.root_config = QConfigNode.coerce(root_config)

    @report_thread_error
    def index_to_node(self, index: QtCore.QModelIndex = QtCore.QModelIndex()) -> QConfigNode:
        """ Internal helper method """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_config

    #-----------
    # Overloaded ItemModel Read Functions
    @report_thread_error
    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        parent_node = self.index_to_node(parent)
        return parent_node.qt_row_count()

    @report_thread_error
    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        parent_node = self.index_to_node(parent)
        return parent_node.qt_col_count()

    @report_thread_error
    def data(self, index: QtCore.QModelIndex, role: int = _Qt.DisplayRole) -> Any:
        """
        Returns the data stored under the given role
        for the item referred to by the index.
        """
        if not index.isValid():
            return None
        # Specify CheckState Role:
        flags = self.flags(index)
        if role == _Qt.CheckStateRole:
            if flags & _Qt.ItemIsUserCheckable:
                node = self.index_to_node(index)
                data = node.qt_get_data(index.column())
                return _Qt.Checked if data else _Qt.Unchecked
        if role != _Qt.DisplayRole and role != _Qt.EditRole:
            return None
        node = self.index_to_node(index)
        data = node.qt_get_data(index.column())
        if isinstance(data, float):
            LOCALE = QtCore.QLocale()
            var = LOCALE.toString(float(data), format='g', precision=6)
        else:
            var = data
        return str(var)

    @report_thread_error
    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = _Qt.EditRole) -> bool:
        """Sets the role data for the item at index to value."""
        if role == _Qt.EditRole:
            data = value
        elif role == _Qt.CheckStateRole:
            data = (value == _Qt.Checked)
        else:
            return False
        node = self.index_to_node(index)
        old_data = node.qt_get_data(index.column())
        if old_data != data:
            node.qt_set_value(data)
        self.dataChanged.emit(index, index)
        return True

    @report_thread_error
    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        """Returns the index of the item in the model specified
        by the given row, column and parent index."""
        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()
        parent_node = self.index_to_node(parent)
        child_node = parent_node.children.iloc[row]
        if child_node:
            new_index = self._new_index(row, column, child_node)
            return new_index
        else:
            return QtCore.QModelIndex()

    def _new_index(self, row: int, col: int, node: QConfigNode) -> QtCore.QModelIndex:
        # Not sure if this is the correct way to register persistent
        # indexes of the model into the backend data structure.
        new_index = self.createIndex(row, col, node)
        new_pindex = QtCore.QPersistentModelIndex(new_index)
        node.qt_set_persistant_index(new_pindex, self)
        return new_index

    @report_thread_error
    def parent(self, child: Optional[QtCore.QModelIndex] = None) -> Any:
        """Returns the parent of the model item with the given index.
        If the item has no parent, an invalid QModelIndex is returned."""
        if child is None:  # Overload with QtCore.QObject.parent()
            return QtCore.QObject.parent(self)
        if not child.isValid():
            return QtCore.QModelIndex()
        node = self.index_to_node(child)
        parent_node = node.qt_get_parent()
        if parent_node is None or parent_node == self.root_config:
            return QtCore.QModelIndex()
        row = parent_node.qt_parents_index_of_me()
        if row is None:
            return QtCore.QModelIndex()
        return self._new_index(row, 0, parent_node)

    @report_thread_error
    def flags(self, index: QtCore.QModelIndex) -> Any:
        """Returns the item flags for the given index."""
        if index.column() == 0:
            # The First Column is just a label and unchangable
            return _Qt.ItemIsEnabled | _Qt.ItemIsSelectable
        if not index.isValid():
            return _Qt.ItemFlag(0)
        child_node = self.index_to_node(index)
        if child_node:
            if child_node.qt_is_editable():
                if child_node.qt_type() is bool:
                    return _Qt.ItemIsEnabled | _Qt.ItemIsUserCheckable
                else:
                    return _Qt.ItemIsEditable | _Qt.ItemIsEnabled | _Qt.ItemIsSelectable
        return _Qt.ItemFlag(0)

    @report_thread_error
    def headerData(self, section: int, orientation: Any, role: int = _Qt.DisplayRole) -> Any:
        if orientation == _Qt.Horizontal and role == _Qt.DisplayRole:
            if section == 0:
                return 'Key'
            if section == 1:
                return 'Value'
        return None


class DelegateStyle(Enum):
    # TODO: does Qt have enums for this?
    NONE = 0
    COMBO_BOX = 1
    SPINNER = 2


class QConfigValueDelegate(QtWidgets.QStyledItemDelegate):
    """
    Determines what editor style is used for a widget displaying a QConfigNode

    References:
        http://stackoverflow.com/questions/28037126/how-to-use-qcombobox-as-delegate-with-qtableview
        http://www.qtcentre.org/threads/41409-PyQt-QTableView-with-comboBox
        http://stackoverflow.com/questions/28680150/qtableview-data-in-background--cell-is-edited
        https://forum.qt.io/topic/46628/qtreeview-with-qitemdelegate-and-qcombobox-inside-not-work-propertly/5
        http://stackoverflow.com/questions/33990029/what-are-the-mechanics-of-the-default-delegate-for-item-views-in-qt
        http://www.qtcentre.org/archive/index.php/t-64165.html
        http://doc.qt.io/qt-4.8/style-reference.html

    """
    def paint(self, painter: Any, option: Any, index: QtCore.QModelIndex) -> Any:
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            model = cast(Any, index.model())
            curent_value = str(model.data(index))
            style = cast(Any, QtWidgets.QApplication.style())
            opt = QtWidgets.QStyleOptionComboBox()

            opt.currentText = curent_value
            opt.rect = option.rect
            opt.editable = False
            opt.frame = True

            if leaf_node.qt_is_editable():
                opt.state |= style.State_On
                opt.state |= style.State_Enabled
                opt.state = style.State_Enabled | style.State_Active

            element = _QStyle.CE_ComboBoxLabel
            control = _QStyle.CC_ComboBox

            style.drawComplexControl(control, opt, painter)
            style.drawControl(element, opt, painter)
        else:
            return super().paint(painter, option, index)

    def createEditor(self, parent: Any, option: Any, index: QtCore.QModelIndex) -> Any:
        """
        Creates different editors for different types of data
        """
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            options = leaf_node.choices
            model = cast(Any, index.model())
            curent_value = model.data(index)
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
            model = cast(Any, index.model())
            curent_value = model.data(index)
            editor.setValue(curent_value)
        else:
            raw_editor = super().createEditor(parent, option, index)
            editor = cast(Any, raw_editor)
            editor.setAutoFillBackground(True)
            # editor.keyPressEvent
        return editor

    def setEditorData(self, editor: Any, index: QtCore.QModelIndex) -> None:
        leaf_node = index.internalPointer()
        delegate_style = None if leaf_node is None else leaf_node.qt_delegate_style()
        if delegate_style == DelegateStyle.COMBO_BOX:
            editor.blockSignals(True)
            model = cast(Any, index.model())
            current_data = model.data(index)
            editor.setCurrentValue(current_data)
            editor.blockSignals(False)
        else:
            return super().setEditorData(editor, index)

    def setModelData(self, editor: Any, model: Any, index: QtCore.QModelIndex) -> None:
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

    def currentIndexChanged(self, combo_idx: int) -> None:
        sender = self.sender()
        self.commitData.emit(sender)

    def updateEditorGeometry(self, editor: Any, option: Any, index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def editorEvent(self, event: Any, model: Any, option: Any, index: QtCore.QModelIndex) -> Any:
        return super().editorEvent(event, model, option, index)

    def eventFilter(
            self, object: Optional[QtCore.QObject],
            event: Optional[QtCore.QEvent],
    ) -> bool:
        return super().eventFilter(object, event)


class QConfigWidget(QtWidgets.QWidget):
    """
    A widget that displays an editable configuration tree.

    Shows the QConfigNode in a QTreeView using a QConfigModel
    """

    data_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent: Any, config: Optional[QConfigNode] = None) -> None:
        import operator
        from functools import reduce
        super().__init__(parent=parent)
        self.config_model = QConfigModel(config)

        self.vert_layout = QtWidgets.QVBoxLayout(self)
        self.tree_view = QtWidgets.QTreeView(self)
        self.tree_view.setObjectName('tree_view')

        self.delegate = QConfigValueDelegate(self.tree_view)
        self.tree_view.setItemDelegateForColumn(1, self.delegate)

        self.tree_view.setModel(self.config_model)
        tree_header = cast(Any, self.tree_view.header())
        tree_header.resizeSection(0, 250)

        self.vert_layout.addWidget(self.tree_view)

        self.tree_view.expandAll()

        self.config_model.dataChanged.connect(self._on_change)

        edit_triggers = reduce(operator.__or__, [
            QtWidgets.QAbstractItemView.CurrentChanged,
            QtWidgets.QAbstractItemView.DoubleClicked,
            QtWidgets.QAbstractItemView.SelectedClicked,
            # QtWidgets.QAbstractItemView.EditKeyPressed,
            # QtWidgets.QAbstractItemView.AnyKeyPressed,
        ])
        self.tree_view.setEditTriggers(edit_triggers)
        self.tree_view.setModel(self.config_model)
        view_header = cast(Any, self.tree_view.header())
        self.tree_view.setHorizontalScrollBarPolicy(_Qt.ScrollBarAsNeeded)
        self.tree_view.resizeColumnToContents(0)
        self.tree_view.resizeColumnToContents(1)
        view_header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def _on_change(self, top_left: Any, bottom_right: Any) -> None:
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
    button_pressed = QtCore.pyqtSignal(MouseEvent)
    key_pressed = QtCore.pyqtSignal(KeyEvent)
    picked = QtCore.pyqtSignal(PickEvent)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # from plottool_ibeis.interactions import zoom_factory, pan_factory
        # from plottool_ibeis import abstract_interaction
        super().__init__(*args, **kwargs)
        from matplotlib.figure import Figure
        # Create unmanaged figure and a canvas
        self.fig = Figure()
        fig_dynamic = cast(Any, self.fig)
        fig_dynamic._no_raise_plottool_ibeis = True
        self.canvas = backend_qt.FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.canvas)

        # Workaround key_press bug
        # References: https://github.com/matplotlib/matplotlib/issues/707
        self.canvas.setFocusPolicy(_Qt.ClickFocus)

        # self.ax = self.fig.add_subplot(1, 1, 1)
        # pt.adjust_subplots(left=0, right=1, top=1, bottom=0, fig=self.fig)
        # if pan_and_zoom or True:
        #     self.pan_events = pan_factory(self.ax)
        #     self.zoon_events = zoom_factory(self.ax)
        self.fig.canvas.mpl_connect('button_press_event', self.button_pressed.emit)
        self.fig.canvas.mpl_connect('key_press_event', self.key_pressed.emit)
        self.fig.canvas.mpl_connect('pick_event', self.picked.emit)

        # self.MOUSE_BUTTONS = abstract_interaction.AbstractInteraction.MOUSE_BUTTONS
        self.setMinimumHeight(20)
        self.setMinimumWidth(20)

        self.installEventFilter(self.parent())


class AdjustWidget(QtWidgets.QWidget):
    """
    A custom widget containing a QConfigWidget for robust normalization
    parameters and a Matplotlib Widget to view those parameters are doing.
    """

    def __init__(self, config: Any = None, raw_img: Any = None) -> None:
        super().__init__()
        self.raw_img = raw_img
        self.processed_img = raw_img
        self.config = QConfigNode.coerce(config)

        main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(main_layout)

        splitter = QtWidgets.QSplitter(parent=self)
        splitter.setOrientation(_Qt.Vertical)
        splitter.sizePolicy().setVerticalStretch(1)
        main_layout.addWidget(splitter)

        self.main_layout = main_layout
        self.splitter = splitter

        self.mpl_widget = MatplotlibWidget(parent=self)
        self.config_widget = QConfigWidget(parent=self, config=self.config)

        self.splitter.addWidget(self.mpl_widget)
        self.splitter.addWidget(self.config_widget)

        self.config_widget.data_changed.connect(self.update_normalization)
        self.mpl_widget.button_pressed.connect(self.on_mpl_widget_click)
        self.update_normalization()

    def update_normalization(self, key: Any = None) -> None:
        import seaborn as sns
        import kwarray
        import numpy as np
        from kwplot.util_seaborn import _weighted_auto_bins
        import pandas as pd

        print('Update Norm')
        params = self.config.to_indexable()
        print('params = {}'.format(ub.urepr(params, nl=1)))


        cropstr = params.get('crop', 'null')
        sl = parse_cropstr(cropstr)
        if sl is not None:
            self.processed_img = self.raw_img[sl]
        else:
            self.processed_img = self.raw_img

        expr = params.get('expr', 'img')
        if expr == 'null' or not expr:
            expr = None
        if expr is not None:
            # Hack: not safe
            img = self.processed_img
            ns = globals().copy()
            ns.update(locals())
            self.processed_img = eval(expr, ns)
            # self.processed_img = ns['img']

        norm_param_names = {
            'scaling', 'extrema', 'low', 'mid', 'high'
        }
        normalizer_params = ub.udict(params) & norm_param_names
        norm_img, norm_info = kwarray.robust_normalize(self.processed_img, params=normalizer_params, return_info=True)

        processed_stats = kwarray.stats_dict(self.processed_img)
        norm_stats = kwarray.stats_dict(norm_img)
        print(f'processed_stats = {ub.urepr(processed_stats, nl=1)}')
        print(f'norm_stats = {ub.urepr(norm_stats, nl=1)}')

        self.norm_img = norm_img
        self.norm_info = norm_info
        print('norm_info = {}'.format(ub.urepr(norm_info, nl=1)))
        print(self.norm_img.sum())

        fig = self.mpl_widget.fig

        fig.clf()
        nSubplots = 2
        SHOW_NORM_HIST = True
        if SHOW_NORM_HIST:
            nSubplots += 1
        ax1 = fig.add_subplot(1, nSubplots, 1)
        ax2 = fig.add_subplot(1, nSubplots, 2)
        if SHOW_NORM_HIST:
            ax3 = fig.add_subplot(1, nSubplots, 3)

        imshow_params = {}
        cmap = params.get('cmap', None)
        if cmap is not None and cmap.lower() not in {'null', 'none'}:
            imshow_params['cmap'] = cmap
        ax1.imshow(self.norm_img, **imshow_params)
        ax1.grid(False)

        counts, bins = np.histogram(self.processed_img, bins=256)
        centers = (bins[1:] + bins[0:-1]) / 2
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
        sns.histplot(ax=ax2, data=data, **hist_data_kw_, **hist_style_kw)

        mid_val = self.norm_info['mid_val']
        max_val = self.norm_info['max_val']
        min_val = self.norm_info['min_val']
        ymin, ymax = ax2.get_ylim()

        ax2.plot([min_val, min_val], [ymin, ymax], '-', color='blue')
        ax2.plot([mid_val, mid_val], [ymin, ymax], '-', color='blue')
        ax2.plot([max_val, max_val], [ymin, ymax], '-', color='blue')

        if SHOW_NORM_HIST:
            counts, bins = np.histogram(self.norm_img, bins=256)
            centers = (bins[1:] + bins[0:-1]) / 2
            data = pd.DataFrame({'value': centers, 'weight': counts})
            n_equal_bins = _weighted_auto_bins(data, 'value', 'weight')
            hist_data_kw = dict(
                x='value',
                weights='weight',
                bins=n_equal_bins,
            )
            hist_style_kw = dict(
            )
            hist_data_kw_ = hist_data_kw.copy()
            sns.histplot(ax=ax3, data=data, **hist_data_kw_, **hist_style_kw)

        fig.canvas.draw()

    def on_mpl_widget_click(self, event: Optional[MouseEvent]) -> None:
        from scipy import stats
        # Let the user click to move the config
        in_axis = event is not None and (event.inaxes is not None and event.xdata is not None)
        if not in_axis:
            return
        # find the closet one to move (todo: cleanup)
        config = self.config
        keys = ['low', 'mid', 'high']
        qarr = [config.children[k].value for k in keys]

        raw_data = self.processed_img.ravel().copy()
        raw_data.sort()

        clicked_percentile = stats.percentileofscore(raw_data, event.xdata)
        clicked_quantile = clicked_percentile / 100.
        idx = ((qarr - clicked_quantile) ** 2).argmin()
        key = keys[idx]

        # I'm not sure if this is the correct way to notify the data model
        # that one of its items has changed, but it does seem to work.
        node = config.children[key]
        for observer in node.qt_observers():
            pindex = node.qt_get_persistant_index(observer)
            index = QtCore.QModelIndex(pindex)
            model = cast(Any, index.model())
            model.setData(index, clicked_quantile)


def parse_cropstr(cropstr: str, error_policy: str = 'return-none') -> Optional[Tuple[slice, slice]]:
    """
    Parse a string of the form R1:R2,C1:C2 into a tuple of slices using regex.

    Args:
        cropstr: A string specifying row and column ranges in format "R1:R2,C1:C2"
                (empty values mean unbounded, e.g. "10:, :20" means from 10 to end,
                and from beginning to 20)

    Returns:
        A tuple of slice objects (row_slice, col_slice)

    Example:
        >>> # xdoctest: +REQUIRES(module:PyQt5)
        >>> parse_cropstr("null")
        None
        >>> parse_cropstr("")
        (slice(None, None, None), slice(None, None, None))
        >>> parse_cropstr("10:20,30:40")
        (slice(10, 20), slice(30, 40))
        >>> parse_cropstr(":20,30:")
        (slice(None, 20), slice(30, None))
    """
    import re
    if not cropstr.strip():
        return (slice(None), slice(None))

    # Regex pattern to match either:
    # 1. empty string (treated as full slice)
    # 2. a single number (e.g. "5" becomes 5:6)
    # 3. a range with start:end (either can be empty)
    pattern = r'^\s*((?P<r1>\d*):(?P<r2>\d*))\s*,\s*((?P<c1>\d*):(?P<c2>\d*))\s*$'

    match = re.fullmatch(pattern, cropstr)
    if not match:
        if error_policy == 'return-none':
            return None
        raise ValueError(f"Invalid crop string format: '{cropstr}'. Expected 'R1:R2,C1:C2'")

    def to_int_or_none(s: str) -> Optional[int]:
        return int(s) if s else None

    r1 = to_int_or_none(match.group('r1'))
    r2 = to_int_or_none(match.group('r2'))
    c1 = to_int_or_none(match.group('c1'))
    c2 = to_int_or_none(match.group('c2'))

    return (slice(r1, r2), slice(c1, c2))


def main(cmdline: bool = True, **kwargs: Any) -> None:
    config = AdjustGuiConfig.cli(cmdline=cmdline, data=kwargs, strict=True)
    print('config = ' + ub.urepr(dict(config), nl=1))

    import sys
    import kwimage
    import seaborn as sns
    sns.set()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('GTK+')

    # https://stackoverflow.com/questions/5160577/ctrl-c-doesnt-work-with-pyqt
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if config.img_fpath is not None:
        raw_img = kwimage.imread(config.img_fpath)
    else:
        raw_img = kwimage.grab_test_image()

    config = {
        'scaling': QConfigNode(config.scaling, choices=['sigmoid', 'linear']),
        'extrema': QConfigNode(config.extrema, choices=['quantile', 'adaptive-quantile', 'iqr', 'iqr-clip']),
        'low': QConfigNode(config.low, min_value=0.0, max_value=1.0, step_value=0.01),
        'mid': QConfigNode(config.mid, min_value=0.0, max_value=1.0, step_value=0.01),
        'high': QConfigNode(config.high, min_value=0.0, max_value=1.0, step_value=0.01),
        'crop': QConfigNode(config.crop),
        'expr': QConfigNode(config.expr),
        'cmap': QConfigNode(config.cmap),
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
