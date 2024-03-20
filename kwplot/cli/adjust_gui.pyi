import scriptconfig as scfg
import ubelt as ub
from PyQt5 import QtCore, QtWidgets
from _typeshed import Incomplete
from collections.abc import Generator
from enum import Enum
from typing import Any

from ubelt.util_const import NoParamType

__docstubs__: str


class AdjustGuiConfig(scfg.DataConfig):
    img_fpath: Incomplete


def report_thread_error(fn):
    ...


class _Indexer:
    func: Incomplete

    def __init__(self, func) -> None:
        ...

    def __getitem__(self, key):
        ...


class IndexedDict(dict):

    def __init__(self, data: Incomplete | None = ..., **kwargs) -> None:
        ...

    def __delitem__(self, key) -> None:
        ...

    def __setitem__(self, key, value) -> None:
        ...

    def update(self, *args, **kwargs) -> None:
        ...

    @property
    def iloc(self):
        ...

    def indexof(self, key):
        ...

    @property
    def index(self):
        ...

    def key_atindex(self, index):
        ...

    def value_atindex(self, index):
        ...


NoValue: NoParamType


class _Qt_ConfigNodeMixin:

    def qt_get_parent(self):
        ...

    def qt_parents_index_of_me(self):
        ...

    def qt_get_child(self, row):
        ...

    def qt_row_count(self):
        ...

    def qt_col_count(self):
        ...

    def qt_get_data(self, column):
        ...

    def qt_type(self):
        ...

    def qt_is_editable(self):
        ...

    value: Incomplete

    def qt_set_value(self, data) -> None:
        ...

    def qt_delegate_style(self):
        ...

    def qt_set_persistant_index(self, index, observer) -> None:
        ...

    def qt_get_persistant_index(self, observer):
        ...

    def qt_observers(self) -> Generator[Any, None, None]:
        ...


class QConfigNode(ub.NiceRepr, _Qt_ConfigNodeMixin):
    parent: Incomplete
    key: Incomplete
    type: Incomplete
    value: Incomplete
    children: Incomplete
    delegate_style: Incomplete
    nullable: Incomplete
    choices: Incomplete
    min_value: Incomplete
    max_value: Incomplete
    step_value: Incomplete

    def __init__(self,
                 value=...,
                 type: Incomplete | None = ...,
                 parent: Incomplete | None = ...,
                 choices: Incomplete | None = ...,
                 min_value: Incomplete | None = ...,
                 max_value: Incomplete | None = ...,
                 step_value: Incomplete | None = ...,
                 nullable: bool = ...,
                 help: Incomplete | None = ...) -> None:
        ...

    def __nice__(self):
        ...

    def add_child(self, key, child: Incomplete | None = ...):
        ...

    def items(self) -> Generator[Any, None, None]:
        ...

    def to_indexable(self):
        ...

    @classmethod
    def coerce(cls, data):
        ...

    @classmethod
    def from_indexable(cls, config):
        ...


class CustomComboBox(QtWidgets.QComboBox):

    def __init__(combo,
                 parent: Incomplete | None = ...,
                 default: Incomplete | None = ...,
                 options: Incomplete | None = ...,
                 changed: Incomplete | None = ...) -> None:
        ...

    def currentValue(combo):
        ...

    def setOptions(combo, options) -> None:
        ...

    def updateOptions(combo,
                      reselect: bool = ...,
                      reselect_index: Incomplete | None = ...) -> None:
        ...

    def setOptionText(combo, option_text_list) -> None:
        ...

    def currentIndexChangedCustom(combo, index) -> None:
        ...

    def setDefault(combo, default: Incomplete | None = ...) -> None:
        ...

    def setCurrentValue(combo, value) -> None:
        ...

    def findValueIndex(combo, value):
        ...


class NullableSpinBox(QtWidgets.QDoubleSpinBox):
    HARD_MIN: Incomplete
    HARD_MAX: Incomplete
    NONE_VALUE: Incomplete
    type: Incomplete
    nullable: Incomplete
    post_nan_value: int

    def __init__(self, *args, **kwargs) -> None:
        ...

    def keyPressEvent(self, event):
        ...

    def setMinimum(self, min_value) -> None:
        ...

    def setMaximum(self, max_value) -> None:
        ...

    def setRange(self, min_value, max_value) -> None:
        ...

    def stepBy(self, steps) -> None:
        ...

    def validate(self, text, pos):
        ...

    def value(self):
        ...

    def setValue(self, value):
        ...

    def valueFromText(self, text):
        ...

    def textFromValue(self, value):
        ...


class QConfigModel(QtCore.QAbstractItemModel):
    root_config: Incomplete

    def __init__(self, root_config, parent: Incomplete | None = ...) -> None:
        ...

    def index_to_node(self, index=...):
        ...

    def rowCount(self, parent=...):
        ...

    def columnCount(self, parent=...):
        ...

    def data(self, qtindex, role=...):
        ...

    def setData(self, qtindex, value, role=...):
        ...

    def index(self, row, col, parent=...):
        ...

    def parent(self, index: Incomplete | None = ...):
        ...

    def flags(self, index):
        ...

    def headerData(self, section, orientation, role=...):
        ...


class DelegateStyle(Enum):
    NONE: int
    COMBO_BOX: int
    SPINNER: int


class QConfigValueDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        ...

    def createEditor(self, parent, option, index):
        ...

    def setEditorData(self, editor, index):
        ...

    def setModelData(self, editor, model, index):
        ...

    def currentIndexChanged(self, combo_idx) -> None:
        ...

    def updateEditorGeometry(self, editor, option, index) -> None:
        ...

    def editorEvent(self, event, model, option, index):
        ...

    def eventFilter(self, editor, event):
        ...


class QConfigWidget(QtWidgets.QWidget):
    data_changed: Incomplete
    config_model: Incomplete
    vert_layout: Incomplete
    tree_view: Incomplete
    delegate: Incomplete

    def __init__(self, parent, config: Incomplete | None = ...) -> None:
        ...


class MatplotlibWidget(QtWidgets.QWidget):
    button_pressed: Incomplete
    key_pressed: Incomplete
    picked: Incomplete
    fig: Incomplete
    canvas: Incomplete

    def __init__(self, *args, **kwargs) -> None:
        ...


class AdjustWidget(QtWidgets.QWidget):
    raw_img: Incomplete
    config: Incomplete
    main_layout: Incomplete
    splitter: Incomplete
    mpl_widget: Incomplete
    config_widget: Incomplete

    def __init__(self,
                 config: Incomplete | None = ...,
                 raw_img: Incomplete | None = ...) -> None:
        ...

    norm_img: Incomplete
    norm_info: Incomplete

    def update_normalization(self, key: Incomplete | None = ...) -> None:
        ...

    def on_mpl_widget_click(self, event) -> None:
        ...


def main(cmdline: int = ..., **kwargs) -> None:
    ...
