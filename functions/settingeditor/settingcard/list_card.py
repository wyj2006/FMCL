from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import FluentIcon

from . import dispatch_card
from .card_header import CardHeader
from .setting_adder import SettingAdder
from .setting_card import SettingCard
from .ui_list_card import Ui_ListCard


class ListCard(SettingCard, Ui_ListCard):
    def _init(self):
        self.setupUi(self)
        self.add_button.setIcon(FluentIcon.ADD.icon())

        self.cards: list[tuple[CardHeader, SettingCard]] = []
        self.element: list = self.getter()
        self.element_attr: list[dict] = self.attr_getter("element_attr", list())
        self.setupCards()

        self.valueChanged.connect(self.on_ListCard_valueChanged)
        self.attrChanged.connect(self.on_ListCard_attrChanged)

    def setupCards(self):
        while self.cards:
            self.removeCard(0)
        for i in range(len(self.element)):
            self.addCard(i)
            QApplication.processEvents()

    @pyqtSlot(object)
    def on_ListCard_valueChanged(self, value: list):
        # 这个函数是为了在值改变时更新自己的cards, 以保证同步
        # 但如果值没有发生改变, 那么就无需同步了, 这个函数就没有执行的必要了
        # 因为子card的getter,setter都是会直接更改self.element的,
        # 所以如果该信号由子card发出, value一定等于self.element,
        # 而信号由子card发出同时也意味着子card本身就已经同步了,
        # 也就没有执行的必要
        # attrChanged和DictCard的相关槽函数同理
        if self.element == value:
            return
        # 因为没法保证顺序, 所以不能像DictCard那样处理
        self.element = value
        self.setupCards()

    @pyqtSlot(str, object)
    def on_ListCard_attrChanged(self, attr_name, value):
        if attr_name != "element_attr":
            return
        if self.element_attr == value:
            return
        self.element_attr = value
        self.setupCards()

    def delete(self, index: int, confirmed=True):
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
        self.removeCard(index)
        self.element.pop(index)
        self.element_attr.pop(index)
        # 在这种情况下, 自己对这两个信号并不会做什么
        self.valueChanged.emit(self.element)
        self.attrChanged.emit("element_attr", self.element_attr)

    def moveDown(self, index: int):
        if index == len(self.element) - 1:
            return
        # 因为需要同步card, 所以不能直接更改
        element = self.element[:]
        element_attr = self.element_attr[:]
        element[index], element[index + 1] = element[index + 1], element[index]
        element_attr[index], element_attr[index + 1] = (
            element_attr[index + 1],
            element_attr[index],
        )
        self.valueChanged.emit(element)
        self.attrChanged.emit("element_attr", element_attr)

    def moveUp(self, index: int):
        if index == 0:
            return
        # 因为需要同步card, 所以不能直接更改
        element = self.element[:]
        element_attr = self.element_attr[:]
        element[index], element[index - 1] = element[index - 1], element[index]
        element_attr[index], element_attr[index - 1] = (
            element_attr[index - 1],
            element_attr[index],
        )
        self.valueChanged.emit(element)
        self.attrChanged.emit("element_attr", element_attr)

    def addCard(self, index: int):
        header, card = self.makeElementCard(index)
        self.element_layout.addRow(header, card)
        self.cards.append((header, card))

    def removeCard(self, index: int):
        header, card = self.cards.pop(index)
        header.deleteLater()
        card.deleteLater()

    def makeElementCard(self, index: int) -> tuple[CardHeader, SettingCard]:
        while index >= len(self.element_attr):
            self.element_attr.append(dict())

        getter = lambda: self.element[index]
        attr_getter = lambda attr_name, default=None: (
            self.element_attr[index].get(attr_name, default)
        )

        def setter(value):
            self.element[index] = value

        def attr_setter(attr_name, value):
            self.element_attr[index][attr_name] = value

        card_header = CardHeader()
        card_header.label.setText(str(index))
        card_header.delete_button.clicked.connect(lambda: self.delete(index, False))
        card_header.movedown_button.clicked.connect(lambda: self.moveDown(index))
        card_header.moveup_button.clicked.connect(lambda: self.moveUp(index))

        card = dispatch_card(getter, attr_getter, setter, attr_setter)
        card.valueChanged.connect(lambda: self.valueChanged.emit(self.element))
        card.attrChanged.connect(
            lambda: self.attrChanged.emit("element_attr", self.element_attr)
        )
        return card_header, card

    @pyqtSlot(bool)
    def on_add_button_clicked(self, _):
        value_adder = SettingAdder(self)
        value_adder.index_editor.setMaximum(len(self.element))
        value_adder.index_editor.setValue(len(self.element))
        if value_adder.exec() == 0:
            return
        index = value_adder.index_editor.value()
        value = value_adder.value
        attr = value_adder.attr
        # 因为需要同步card, 所以不能直接更改
        element = self.element[:index] + [value] + self.element[index:]
        element_attr = self.element_attr[:index] + [attr] + self.element_attr[index:]
        self.valueChanged.emit(element)
        self.attrChanged.emit("element_attr", element_attr)
