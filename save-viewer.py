import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import json

CRYPTO_KEY = "hE0+JOzhYLBPOqXmb43vj5+DUigTMjmUu4j3zWNb3LI="
CRYPTO_IV = "fvaCYFNydvipQUqTlD9yXg=="

def decrypt_file(file_path, cryptoKey, cryptoIV):
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    aes_key = base64.b64decode(cryptoKey)
    aes_iv = base64.b64decode(cryptoIV)

    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    decrypted_bytes = cipher.decrypt(file_bytes)
    decrypted_bytes = unpad(decrypted_bytes, AES.block_size)

    json_string = decrypted_bytes.decode("utf-8")

    return json_string

def encrypt_file(file_path, json_string, cryptoKey, cryptoIV):
    aes_key = base64.b64decode(cryptoKey)
    aes_iv = base64.b64decode(cryptoIV)

    json_bytes = json_string.encode("utf-8")
    padded_bytes = pad(json_bytes, AES.block_size)

    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    encrypted_bytes = cipher.encrypt(padded_bytes)

    with open(file_path, "wb") as f:
        f.write(encrypted_bytes)

class TreeItem:
    """A Json item corresponding to a line in QTreeView"""

    def __init__(self, parent: "TreeItem" = None):
        self._parent = parent
        self._key = ""
        self._value = ""
        self._value_type = None
        self._children = []

    def appendChild(self, item: "TreeItem"):
        """Add item as a child"""
        self._children.append(item)

    def child(self, row: int) -> "TreeItem":
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> "TreeItem":
        """Return the parent of the current item"""
        return self._parent

    def childCount(self) -> int:
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self) -> int:
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    @property
    def key(self) -> str:
        """Return the key name"""
        return self._key

    @key.setter
    def key(self, key: str):
        """Set key name of the current item"""
        self._key = key

    @property
    def value(self) -> str:
        """Return the value name of the current item"""
        return self._value

    @value.setter
    def value(self, value: str):
        """Set value name of the current item"""
        self._value = value

    @property
    def value_type(self):
        """Return the python type of the item's value."""
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        """Set the python type of the item's value."""
        self._value_type = value

    @classmethod
    def load(
        cls, value: list | dict, parent: "TreeItem" = None, sort=True
    ) -> "TreeItem":
        """Create a 'root' TreeItem from a nested list or a nested dictonary

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = TreeItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            TreeItem: TreeItem
        """
        rootItem = TreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = index
                child.value_type = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.value_type = type(value)

        return rootItem


class JsonModel(QAbstractItemModel):
    """ An editable model of Json data """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("key", "value")

    def clear(self):
        """ Clear data from the model """
        self.load({})

    def load(self, document: dict):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = str(value)

                self.dataChanged.emit(index, index, [Qt.ItemDataRole.EditRole])

                return True

        return False

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override from QAbstractItemModel

        For the JsonModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """

        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(JsonModel, self).flags(index)

        if index.column() == 1:
            return Qt.ItemIsEditable | flags
        else:
            return flags

    def to_json(self, item=None):

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_json(ch)
            return document

        elif item.value_type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document

        else:
            return item.value

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filePath = None
        self.fileContent = None
        self.contentObject = None

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("File")

        openAction = QAction("Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open a save file")
        openAction.triggered.connect(self.openSaveFile)

        self.saveAction = QAction("Save", self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip("Save the current save file")
        self.saveAction.setEnabled(False)
        self.saveAction.triggered.connect(self.saveSaveFile)

        self.saveAsAction = QAction("Save As", self)
        self.saveAsAction.setStatusTip("Save the current save file as a new file")
        self.saveAsAction.setEnabled(False)
        self.saveAsAction.triggered.connect(self.saveSaveFileAs)

        self.viewRawAction = QAction("View Raw", self)
        self.viewRawAction.setShortcut("Ctrl+R")
        self.viewRawAction.setStatusTip("View the raw save file")
        self.viewRawAction.setEnabled(False)
        self.viewRawAction.triggered.connect(self.openSaveFileRaw)

        exitAction = QAction("Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit the application")
        exitAction.triggered.connect(qApp.quit)

        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.viewRawAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        self.noFileLabel = QLabel("No save file opened")
        self.noFileLabel.setAlignment(Qt.AlignCenter)
        self.noFileLabel.setStyleSheet("color: gray; font-size: 16px; font-weight: bold")

        self.noFileLabelDescription = QLabel("Open a save file to view its contents")
        self.noFileLabelDescription.setAlignment(Qt.AlignCenter)
        self.noFileLabelDescription.setStyleSheet("color: gray; font-size: 12px")

        self.noFileLayout = QVBoxLayout()
        self.noFileLayout.setAlignment(Qt.AlignCenter)
        self.noFileLayout.addWidget(self.noFileLabel)
        self.noFileLayout.addWidget(self.noFileLabelDescription)

        self.noFileWidget = QWidget()
        self.noFileWidget.setLayout(self.noFileLayout)
        
        self.saveContentWidget = QWidget()
        self.saveContentWidget.hide()

        self.saveContentLayout = QVBoxLayout()
        self.saveContentLayout.setAlignment(Qt.AlignTop)

        self.saveContentWidget.setLayout(self.saveContentLayout)

        self.saveContentTitle = QLabel("Save Content")
        self.saveContentTitle.setStyleSheet("font-size: 16px; font-weight: bold")

        self.saveContentView = QTreeView()
        
        self.model = JsonModel()
        self.saveContentView.setModel(self.model)

        self.saveContentLayout.addWidget(self.saveContentTitle)
        self.saveContentLayout.addWidget(self.saveContentView)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.noFileWidget)
        mainLayout.addWidget(self.saveContentWidget)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.setWindowTitle("The Maze Project Save Viewer")
        self.resize(750, 450)

    def openSaveFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Save File", "", "Save Files (*.save)")

        if fileName:
            self.filePath = fileName
            self.fileContent = decrypt_file(fileName, CRYPTO_KEY, CRYPTO_IV)
            self.contentObject = json.loads(self.fileContent)
            self.refreshViewer()

    def saveSaveFile(self):
        if self.fileContent:
            content = json.dumps(self.model.to_json())
            encrypt_file(self.filePath, content, CRYPTO_KEY, CRYPTO_IV)

    def saveSaveFileAs(self):
        if self.fileContent:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Save File", "", "Save Files (*.save)")

            if fileName:
                content = json.dumps(self.model.to_json())
                encrypt_file(fileName, content, CRYPTO_KEY, CRYPTO_IV)
                self.filePath = fileName

    def openSaveFileRaw(self):
        if self.fileContent:
            dialog = QDialog(self)
            dialog.setWindowTitle("Raw Save File")
            dialog.setWindowModality(Qt.ApplicationModal)
            dialog.resize(400, 300)

            textEdit = QTextEdit()
            textEdit.setText(self.fileContent)
            textEdit.setReadOnly(True)

            layout = QVBoxLayout(dialog)
            layout.addWidget(textEdit)

            dialog.exec_()

    def refreshViewer(self):
        if self.fileContent:
            self.noFileWidget.hide()
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.viewRawAction.setEnabled(True)

            fileName = os.path.basename(self.filePath)
            self.saveContentTitle.setText(f"Save Content: {fileName}")

            self.model.load(self.contentObject)
            self.saveContentWidget.show()
        else:
            self.noFileLabel.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


main()