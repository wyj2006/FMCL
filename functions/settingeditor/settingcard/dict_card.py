from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import FluentIcon

from . import dispatch_card
from .card_header import CardHeader
from .setting_adder import SettingAdder
from .setting_card import SettingCard
from .ui_dict_card import Ui_DictCard


class DictCard(SettingCard, Ui_DictCard):
    def _init(self):
        self.setupUi(self)
        self.add_button.setIcon(FluentIcon.ADD.icon())

        self.cards: dict[str, tuple[CardHeader, SettingCard]] = {}
        self.pair: dict = self.getter()
        self.pair_attr: dict[str, dict] = self.attr_getter("pair_attr", dict())
        self.setupCards()

        self.valueChanged.connect(self.on_DictCard_valueChanged)
        self.attrChanged.connect(self.on_DictCard_attrChanged)

    def setupCards(self):
        while self.cards:
            self.cards.pop(self.cards.keys()[0]).deleteLater()
        for key in self.pair:
            self.addCard(key)
            QApplication.processEvents()

    @pyqtSlot(object)
    def on_DictCard_valueChanged(self, value: dict):
        if self.pair == value:
            return
        for key in tuple(self.pair):
            if key not in value:  # 键值对被删除
                self.removeCard(key)
                self.pair.pop(key)
        for key in value:
            if key not in self.pair:  # 新增键值对
                self.pair[key] = value[key]
                self.addCard(key)
            elif self.pair[key] != value[key]:
                # 重新创建一个以防类型改变
                self.removeCard(key)
                self.addCard(key)
                self.pair[key] = value[key]
                QApplication.processEvents()

    @pyqtSlot(str, object)
    def on_DictCard_attrChanged(self, attr_name, value):
        if attr_name != "pair_attr":
            return
        if self.pair_attr == value:
            return
        self.pair_attr = value
        self.setupCards()

    def delete(self, key: str, confirmed=True):
        if not confirmed:
            if (
                QMessageBox.question(
                    self,
                    self.tr("删除确认"),
                    self.tr("确认删除?"),
                    buttons=QMessageBox.StandardButton.Ok
                    | QMessageBox.StandardButton.Cancel,
                )
                != QMessageBox.StandardButton.Ok
            ):
                return
        self.removeCard(key)
        self.pair.pop(key)
        self.pair_attr.pop(key)
        # 在这种情况下, 自己对这两个信号并不会做什么
        self.valueChanged.emit(self.pair)
        self.attrChanged.emit("pair_attr", self.pair_attr)

    def addCard(self, key: str):
        header, card = self.makePairCard(key)
        self.pair_layout.addRow(header, card)
        self.cards[key] = (header, card)

    def removeCard(self, key: str):
        header, card = self.cards.pop(key)
        header.deleteLater()
        card.deleteLater()

    def makePairCard(self, key: str) -> tuple[Ui_DictCard, SettingCard]:
        if key not in self.pair_attr:
            self.pair_attr[key] = {}

        getter = lambda: self.pair[key]
        attr_getter = lambda attr_name, default=None: self.pair_attr[key].get(
            attr_name, default
        )

        def setter(value):
            self.pair[key] = value

        def attr_setter(attr_name, value):
            self.pair[key][attr_name] = value

        card_header = CardHeader()
        card_header.label.setText(key)
        card_header.movedown_button.hide()
        card_header.moveup_button.hide()
        card_header.delete_button.clicked.connect(lambda: self.delete(key, False))

        card = dispatch_card(getter, attr_getter, setter, attr_setter)
        card.valueChanged.connect(lambda: self.valueChanged.emit(self.pair))
        card.attrChanged.connect(
            lambda: self.attrChanged.emit("pair_attr", self.pair_attr)
        )
        return card_header, card

    @pyqtSlot(bool)
    def on_add_button_clicked(self, _):
        value_adder = SettingAdder(self)
        i = 1
        while (key := f"key{i}") in self.pair:
            i += 1
        value_adder.key_editor.setPlaceholderText(key)
        if value_adder.exec() == 0:
            return
        key = value_adder.key_editor.text() or key  # 如果没有输入那么使用默认的key
        value = value_adder.value
        attr = value_adder.attr
        # 因为需要同步card, 所以不能直接更改
        self.valueChanged.emit(self.pair | {key: value})
        self.attrChanged.emit("pair_attr", self.pair_attr | {key: attr})
