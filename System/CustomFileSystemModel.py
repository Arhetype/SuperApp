import logging
import os
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt, QFileInfo

logging.basicConfig(filename='super_app.log', level=logging.INFO, format='%(asctime)s - %(message)s')


class CustomFileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.column() == 1:
            fileInfo = QFileInfo(self.filePath(index))
            if fileInfo.isDir():
                return self.directorySize(fileInfo.absoluteFilePath())
        return super().data(index, role)

    def directorySize(self, path):
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return self.formatSize(total_size)

    def formatSize(self, size):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(size) < 1024.0:
                return "%3.1f%sB" % (size, unit)
            size /= 1024.0
        return "%.1f%sB" % (size, 'Y')
