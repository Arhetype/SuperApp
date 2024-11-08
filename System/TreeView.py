import logging
import os
import shutil
import subprocess
from datetime import datetime

import psutil
from PyQt5.QtGui import QKeySequence, QDrag
from PyQt5.QtWidgets import (
    QMainWindow, QTreeView, QVBoxLayout, QWidget, QAction,
    QMenu, QMessageBox, QInputDialog, QLineEdit, QPushButton, QToolBar, QShortcut, QApplication, QTextEdit,
    QAbstractItemView,
)
from PyQt5.QtCore import QModelIndex, Qt, QTimer, QMimeData, QUrl

from CustomFileSystemModel import CustomFileSystemModel
from MemoryTaskWindow import MemoryTaskWindow
from SharedMemoryManager import SharedMemoryManager
from TerminalWindow import TerminalWindow


class TreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.dragged_item = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.dragged_item = self.model().filePath(index)
                last_folder_name = os.path.basename(self.dragged_item)
                if last_folder_name.lower() == "корзина" or last_folder_name.lower() == "system":
                    self.dragged_item = None
        super().mousePressEvent(event)

    def startDrag(self, supportedActions):
        if self.dragged_item:
            drag = QDrag(self)
            mime_data = QMimeData()
            urls = [QUrl.fromLocalFile(self.dragged_item)]
            mime_data.setUrls(urls)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

