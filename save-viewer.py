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

        self.saveContentList = QListWidget()
        self.saveContentList.itemDoubleClicked.connect(self.setNewValue)

        self.saveContentLayout.addWidget(self.saveContentTitle)
        self.saveContentLayout.addWidget(self.saveContentList)

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
            encrypt_file(self.filePath, self.fileContent, CRYPTO_KEY, CRYPTO_IV)

    def saveSaveFileAs(self):
        if self.fileContent:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Save File", "", "Save Files (*.save)")

            if fileName:
                encrypt_file(fileName, self.fileContent, CRYPTO_KEY, CRYPTO_IV)
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
            
    def setNewValue(self, listItem):
        property = listItem.text().split(":")[0]
        text, ok = QInputDialog.getText(self, "Set New Value", f"Enter the new value for {property}:")

        if ok:
            self.contentObject[property] = text
            self.fileContent = json.dumps(self.contentObject)
            self.reloadSaveContent()
        
    def reloadSaveContent(self):
        self.saveContentList.clear()

        if self.fileContent:
            fileName = os.path.basename(self.filePath)
            self.saveContentTitle.setText(f"Save: {fileName}")

            for save in self.contentObject:
                content = str(self.contentObject[save])[:100]
                item = QListWidgetItem(f"{save}: {content}")
                self.saveContentList.addItem(item)

    def refreshViewer(self):
        if self.fileContent:
            self.noFileWidget.hide()
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.viewRawAction.setEnabled(True)
            self.saveContentWidget.show()
            self.reloadSaveContent()
        else:
            self.noFileLabel.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


main()