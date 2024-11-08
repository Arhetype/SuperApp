import logging
import os
import shutil

from PyQt5.QtWidgets import QTreeView, QAbstractItemView, QMessageBox
from PyQt5.QtCore import Qt


logging.basicConfig(filename='super_app.log', level=logging.INFO, format='%(asctime)s - %(message)s')
class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        destination_index = self.indexAt(event.pos())
        destination_folder = self.model().filePath(destination_index)

        if not os.path.exists(destination_folder):
            destination_folder = self.get_destination_folder(event.pos())

        if not os.path.isdir(destination_folder):
            QMessageBox.warning(self, "Invalid Drop", "Вы можете перетаскивать только в директории.")
            logging.warning("Недопустимое место для перетаскивания: не директория")
            return

        for url in event.mimeData().urls():
            try:
                self.move_item(url, destination_folder)
                logging.info(f"Файл {url.toLocalFile()} перемещен в {destination_folder}")
            except Exception as e:
                QMessageBox.critical(self, "Error Moving Item", str(e))
                logging.error(f"Ошибка при перемещении файла {url.toLocalFile()} в {destination_folder}: {e}")

        self.model().setRootPath('')  # Обновление модели для отражения изменений
        self.model().setRootPath(destination_folder)

    def move_item(self, url, destination_folder):
        file_name = os.path.basename(url.toLocalFile())
        file_path = str(url.toLocalFile())
        destination_path = os.path.join(destination_folder, file_name)

        if os.path.commonpath([file_path, destination_path]) == os.path.commonpath([file_path]):
            return

        if os.path.exists(file_path):
            if os.path.exists(destination_path) and not os.path.samefile(file_path, destination_path):
                raise Exception(f"Файл '{file_name}' уже существует в целевой папке.")

            if os.path.isdir(file_path):
                shutil.move(file_path, destination_path)
            elif os.path.isfile(file_path):
                shutil.move(file_path, destination_path)

    def get_destination_folder(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return ""
        file_path = self.model().filePath(index)
        if os.path.isdir(file_path):
            return file_path
        return os.path.dirname(file_path)
