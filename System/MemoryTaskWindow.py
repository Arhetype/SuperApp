import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox, QDialog

class MemoryTaskWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Задание по обновлению информации о памяти")
        layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        self.setLayout(layout)

    def update_info(self):
        if self.memory_manager:
            data = self.memory_manager.read(1024).decode('utf-8').strip('\x00')
            self.output_text.setPlainText(data)

    def set_memory_manager(self, memory_manager):
        self.memory_manager = memory_manager
        self.update_info()

