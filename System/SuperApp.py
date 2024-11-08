import logging
import os
import shutil
import subprocess
from datetime import datetime

import psutil
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QMainWindow, QTreeView, QVBoxLayout, QWidget, QAction,
    QMenu, QMessageBox, QInputDialog, QLineEdit, QPushButton, QToolBar, QShortcut, QApplication, QTextEdit,
    QAbstractItemView, QFileDialog,
)
from PyQt5.QtCore import QModelIndex, Qt, QTimer

from CustomFileSystemModel import CustomFileSystemModel
from DeviceHandler import DeviceHandler
from MemoryTaskWindow import MemoryTaskWindow
from SharedMemoryManager import SharedMemoryManager
from TerminalWindow import TerminalWindow
from TreeView import TreeView
from USBManager import USBManager

logging.basicConfig(filename='super_app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class SuperApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.original_paths = {}
        self.clipboard_path = None

        self.initUI()
        self.createTaskAction()

        self.memory_manager = SharedMemoryManager('memory_info.txt', 1024)
        self.memory_task_window_1 = MemoryTaskWindow()
        self.memory_task_window_1.set_memory_manager(self.memory_manager)
        self.memory_task_window_2 = MemoryTaskWindow()
        self.memory_task_window_2.set_memory_manager(self.memory_manager)

        self.timer = QTimer()
        self.timer.timeout.connect(self.executeTask)
        self.timer.start(1000)

        self.original_paths = {}
        self.app_directory = '/home/dan/Superapp'

        self.device_handler = DeviceHandler()
        self.usb_manager = USBManager(self)
        self.usb_manager.start()


    def initUI(self):
        self.setGeometry(300, 300, 804, 630)
        self.setWindowTitle('SuperApp')

        self.createTrash()
        self.createSystemFolder()
        self.createInitialFolders()

        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('Файл')
        about_menu = main_menu.addMenu('О программе')
        applications_menu = main_menu.addMenu('Приложения')

        open_terminal_action = QAction('Терминал Linux', self)
        open_terminal_action.triggered.connect(self.open_system_terminal)
        open_browser_action = QAction('Браузер', self)
        open_browser_action.triggered.connect(self.open_system_browser)
        open_system_monitor_action = QAction('Системный монитор', self)
        open_system_monitor_action.triggered.connect(self.open_system_monitor)
        open_calculator_action = QAction('Калькулятор', self)
        open_calculator_action.triggered.connect(self.open_system_calculator)

        applications_menu.addAction(open_browser_action)
        applications_menu.addAction(open_terminal_action)
        applications_menu.addAction(open_system_monitor_action)
        applications_menu.addAction(open_calculator_action)

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.showAboutInfo)
        about_menu.addAction(about_action)

        create_root_folder_action = QAction('Создать папку в корневой', self)
        create_root_folder_action.triggered.connect(self.createRootFolder)
        create_root_file_action = QAction('Создать файл в корневой', self)
        create_root_file_action.triggered.connect(self.createRootFile)

        file_menu.addAction(create_root_folder_action)
        file_menu.addAction(create_root_file_action)

        self.contextMenu = QMenu(self)

        self.model = CustomFileSystemModel()
        self.model.setRootPath('/home/dan/Superapp')
        self.tree = TreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index('/home/dan/Superapp'))
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.showContextMenu)

        self.tree.setSelectionMode(self.tree.SingleSelection)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.model.setReadOnly(False)

        self.setAcceptDrops(True)


        layout = QVBoxLayout()
        layout.addWidget(self.tree)

        toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Поиск по имени файла")
        toolbar.addWidget(self.searchInput)

        self.searchButton = QPushButton("Поиск")
        toolbar.addWidget(self.searchButton)
        self.searchButton.clicked.connect(self.searchItem)

        self.terminalButton = QPushButton("Терминал")
        toolbar.addWidget(self.terminalButton)
        self.terminalButton.clicked.connect(self.open_system_terminal)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.processes_output = QTextEdit()
        layout.addWidget(self.processes_output)

        # Горячие клавиши
        shortcut_action = QAction("Горячие клавиши", self)
        shortcut_action.triggered.connect(self.show_shortcuts)
        about_menu.addAction(shortcut_action)

        deleteShortcut = QShortcut(QKeySequence.Delete, self)
        deleteShortcut.activated.connect(self.deleteItem)

        ctrlDeleteShortcut = QShortcut(QKeySequence("Ctrl+Delete"), self)
        ctrlDeleteShortcut.activated.connect(self.deleteImmediatelyItem)

        ctrlNShortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        ctrlNShortcut.activated.connect(self.createFileItem)

        ctrlCCopyShortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        ctrlCCopyShortcut.activated.connect(self.copyItem)

        ctrlVPasteShortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        ctrlVPasteShortcut.activated.connect(self.pasteItem)

        ctrlRShortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        ctrlRShortcut.activated.connect(self.renameItem)

        ctrlIRestoreShortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        ctrlIRestoreShortcut.activated.connect(self.restoreItem)

        ctrlCustomTerminalShortcut = QShortcut(QKeySequence("Ctrl+Shift+Alt+T"), self)
        ctrlCustomTerminalShortcut.activated.connect(self.open_custom_terminal)

        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #202020;
                        color: white;
                    }
                    QToolBar {
                        background-color: #303030;
                        border: none;
                    }
                    QPushButton {
                        background-color: #FF5733; /* Красный */
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #E74C3C; /* Более темный красный при наведении */
                    }
                    QLineEdit {
                        background-color: #404040;
                        border: 2px solid #FF5733; /* Красный */
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 16px;
                        color: white;
                    }
                    QTextEdit {
                        background-color: #404040;
                        border: 2px solid #FF5733; /* Красный */
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 16px;
                        color: white;
                    }
                    QMenu {
                        background-color: #404040;
                        border: 1px solid #FF5733; /* Красный */
                        border-radius: 5px;
                        padding: 5px;
                        font-size: 16px;
                        color: white;
                    }
                    QAction {
                        color: #FF5733; /* Красный */
                    }
                    QTreeView {
                        background-color: #303030; /* Цвет фона области с файловой системой */
                        color: white;
                        alternate-background-color: #404040; /* Цвет фона для нечетных строк */
                        border: 2px solid #FF5733; /* Красный */
                        border-radius: 5px;
                        font-size: 16px;
                    }
                """)

    def createTaskAction(self):
        task_action = QAction('Задание', self)
        task_action.triggered.connect(self.openMemoryTaskWindow)

        process_tracking_action = QAction('Отслеживание процессов ОС вне ПО', self)
        process_tracking_action.triggered.connect(self.trackProcesses)

        main_menu = self.menuBar().findChild(QMenu, 'main_menu')
        if not main_menu:
            main_menu = self.menuBar().addMenu('Задание')
            main_menu.setObjectName('main_menu')

        main_menu.addAction(task_action)
        main_menu.addAction(process_tracking_action)

    def openMemoryTaskWindow(self):
        self.memory_task_window_1.show()
        self.memory_task_window_2.show()

    def executeTask(self):
        memory_usage = psutil.virtual_memory().percent
        app_width = self.width()
        app_height = self.height()
        screen_width = QApplication.primaryScreen().size().width()
        screen_height = QApplication.primaryScreen().size().height()
        data = (f'Процент используемой физической памяти: {memory_usage}%\n'
                f'Ширина и высота рамки приложения: {app_width}x{app_height}\n'
                f'Ширина и высота рамки экрана: {screen_width}x{screen_height}').encode('utf-8')
        self.memory_manager.write(data)
        if self.memory_task_window_1.isVisible():
            self.memory_task_window_1.update_info()
        if self.memory_task_window_2.isVisible():
            self.memory_task_window_2.update_info()

    def displayMemoryInfo(self):
        data = self.memory_manager.read(1024).decode('utf-8')
        self.processes_output.setPlainText(data)

    def displayMemoryInfo(self):
        data = self.memory_manager.read(1024).decode('utf-8')
        self.processes_output.setPlainText(data)

    def handle_device_event(self, action, device):
        logging.info(f'Событие USB: {action}, устройство: {device}')
        if action == 'add':
            device_path = device.device_node
            device_name = device.get('ID_FS_LABEL', os.path.basename(device_path))

            # Используем корневую папку SuperApp
            app_directory = '/home/dan/Superapp'
            device_directory = os.path.join(app_directory, device_name)
            os.makedirs(device_directory, exist_ok=True)

            self.original_paths[device_path] = device_directory
            if self.model:
                self.model.setRootPath('')
                self.model.setRootPath(app_directory)
            QMessageBox.information(None, 'Подключено устройство', f"Устройство: {device_name} ({device_path})")

        elif action == 'remove':
            device_path = device.device_node
            if device_path in self.original_paths:
                device_directory = self.original_paths.pop(device_path)
                shutil.rmtree(device_directory, ignore_errors=True)
                if self.model:
                    self.model.setRootPath('')
                    self.model.setRootPath('/home/dan/Superapp')
                QMessageBox.information(None, 'Отключено устройство', f"Устройство: {os.path.basename(device_directory)} ({device_path})")


    def trackProcesses(self):
        logging.info("Отслеживание процессов ОС вне ПО")
        all_processes = psutil.process_iter()

        our_pid = os.getpid()

        other_processes = []

        for process in all_processes:
            try:
                process_info = process.as_dict(attrs=['pid', 'name', 'create_time'])
                pid = process_info['pid']
                process_name = process_info['name']
                create_time = datetime.fromtimestamp(process_info['create_time']).strftime('%Y-%m-%d %H:%M:%S')

                if pid != our_pid:
                    other_processes.append((pid, process_name, create_time))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        self.processes_output.clear()

        log_lines = []
        if other_processes:
            self.processes_output.append("Процессы ОС (без собственных):")
            log_lines.append("Процессы ОС (без собственных):")
            for pid, process_name, create_time in other_processes:
                process_info_line = f"PID: {pid}, Имя процесса: {process_name}, Время создания: {create_time}"
                self.processes_output.append(process_info_line)
                log_lines.append(process_info_line)
        else:
            no_processes_message = "В данный момент нет других процессов ОС."
            self.processes_output.append(no_processes_message)
            log_lines.append(no_processes_message)

        # Ask user for the name of the log file
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "Текстовый файл (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as log_file:
                log_file.write("\n".join(log_lines))

    def show_shortcuts(self):
        logging.info("Показ горячих клавиш")
        QMessageBox.information(self, 'Горячие клавиши',
                                'CTRL + C: Копирование объекта (файл, папка)\n'
                                'CTRL + V: Вставка объекта (файл, папка)\n'
                                'CTRL + Delete: Удаление объекта безвозратно (файл, папка)\n'
                                'CTRL + N: Создание файла в выбранной папке\n'
                                'CTRL + R: Переминования файла или папки\n'
                                'CTRL + I: Восстановления файла или папки из корзины\n'
                                'Ctrl+Shift+Alt+T: Открытие кастомного терминала\n')

    def open_custom_terminal(self):
        logging.info("Открытие кастомного терминала")
        self.terminal = TerminalWindow()
        self.terminal.show()

    def open_system_terminal(self):
        sender_text = self.sender().text()
        logging.info(f"Открытие системного терминала: {sender_text}")
        if self.sender().text() == 'Терминал Linux':
            subprocess.Popen(['terminator'])
        elif self.sender().text() == 'Терминал':
            self.open_custom_terminal()

    def open_system_browser(self):
        logging.info("Открытие системного браузера")
        subprocess.Popen(['xdg-open', 'https://www.google.com/'])

    def open_system_monitor(self):
        logging.info("Открытие системного монитора")
        subprocess.Popen(['gnome-system-monitor'])

    def open_system_calculator(self):
        logging.info("Открытие системного калькулятора")
        subprocess.Popen(['mate-calc'])

    def createTrash(self):
        logging.info("Создание корзины")
        trash_path = os.path.join('/home/dan/Superapp', 'Корзина')
        if not os.path.exists(trash_path):
            os.makedirs(trash_path)

    def createSystemFolder(self):
        logging.info("Создание системной папки")
        system_path = os.path.join('/home/dan/Superapp', 'System')
        if not os.path.exists(system_path):
            os.makedirs(system_path)
            open(os.path.join(system_path, 'placeholder.txt'), 'a').close()

    def createInitialFolders(self):
        logging.info("Создание начальных папок")
        initial_folders = ['folder1', 'folder2']
        for folder in initial_folders:
            folder_path = os.path.join('/home/dan/Superapp', folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    def showAboutInfo(self):
        logging.info("Показ информации о программе")
        QMessageBox.information(self, 'О программе',
                                'Операционные системы и оболочки: RedOS\n'
                                'Язык программирования: Python\n'
                                'ФИО и группа разработчика: Рябцев Даниил ПрИ-23')

    def openItem(self):
        logging.info("Открытие элемента")
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        if os.path.isfile(filePath):
            try:
                os.startfile(filePath)
            except AttributeError:
                import subprocess
                subprocess.run(['xdg-open', filePath])
        else:
            QMessageBox.warning(self, 'Ошибка', 'Это не файл!')

    def showContextMenu(self, pos):
        logging.info("Показ контекстного меню")
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        self.contextMenu.clear()

        if filePath.endswith('/Корзина'):
            clearTrashAction = QAction('Очистить корзину', self)
            clearTrashAction.triggered.connect(self.clearTrash)
            self.contextMenu.addAction(clearTrashAction)
        else:
            if filePath.startswith('/home/dan/Superapp/Корзина'):
                restoreAction = QAction('Восстановить CTRL + I', self)
                restoreAction.triggered.connect(self.restoreItem)
                self.contextMenu.addAction(restoreAction)
                deleteImmediatelyAction = QAction('Удалить сразу CTRL + DELETE', self)
                deleteImmediatelyAction.triggered.connect(self.deleteImmediatelyItem)
                self.contextMenu.addAction(deleteImmediatelyAction)
            elif filePath.endswith('/System'):
                createFolderAction = QAction('Создать папку', self)
                createFolderAction.triggered.connect(self.createFolderItem)
                createFileAction = QAction('Создать файл CTRL + N:', self)
                createFileAction.triggered.connect(self.createFileItem)
                self.contextMenu.addAction(createFolderAction)
                self.contextMenu.addAction(createFileAction)
            else:
                if os.path.isfile(filePath):
                    openAction = QAction('Открыть', self)
                    openAction.triggered.connect(self.openItem)
                    deleteAction = QAction('Удалить DELETE', self)
                    deleteAction.triggered.connect(self.deleteItem)
                    deleteImmediatelyAction = QAction('Удалить сразу CTRL + DELETE', self)
                    deleteImmediatelyAction.triggered.connect(self.deleteImmediatelyItem)
                    renameAction = QAction('Переименовать CTRL + R', self)
                    renameAction.triggered.connect(self.renameItem)
                    copyAction = QAction('Копировать CTRL + C', self)
                    copyAction.triggered.connect(self.copyItem)
                    pasteAction = QAction('Вставить CTRL + V', self)
                    pasteAction.triggered.connect(self.pasteItem)
                    self.contextMenu.addAction(openAction)
                    self.contextMenu.addAction(deleteAction)
                    self.contextMenu.addAction(deleteImmediatelyAction)
                    self.contextMenu.addAction(renameAction)
                    self.contextMenu.addAction(copyAction)
                    self.contextMenu.addAction(pasteAction)
                else:
                    createFolderAction = QAction('Создать папку', self)
                    createFolderAction.triggered.connect(self.createFolderItem)
                    createFileAction = QAction('Создать файл CTRL + N', self)
                    createFileAction.triggered.connect(self.createFileItem)
                    renameAction = QAction('Переименовать CTRL + R', self)
                    renameAction.triggered.connect(self.renameItem)
                    deleteAction = QAction('Удалить DELETE', self)
                    deleteAction.triggered.connect(self.deleteItem)
                    deleteImmediatelyAction = QAction('Удалить сразу CTRL + DELETE', self)
                    deleteImmediatelyAction.triggered.connect(self.deleteImmediatelyItem)
                    copyAction = QAction('Копировать CTRL + C', self)
                    copyAction.triggered.connect(self.copyItem)
                    pasteAction = QAction('Вставить CTRL + V', self)
                    pasteAction.triggered.connect(self.pasteItem)
                    self.contextMenu.addAction(createFolderAction)
                    self.contextMenu.addAction(createFileAction)
                    self.contextMenu.addAction(renameAction)
                    self.contextMenu.addAction(deleteAction)
                    self.contextMenu.addAction(deleteImmediatelyAction)
                    self.contextMenu.addAction(copyAction)
                    self.contextMenu.addAction(pasteAction)

        self.contextMenu.exec_(self.tree.mapToGlobal(pos))


    def createRootFolder(self):
        new_folder_name, ok = QInputDialog.getText(self, "Создание папки в корневой директории", "Введите имя папки:")
        if ok and new_folder_name:
            rootPath = self.model.rootPath()
            new_folder_path = os.path.join(rootPath, new_folder_name)
            if not os.path.exists(new_folder_path):
                logging.info(f"Создана root папка: {new_folder_path}")
                os.makedirs(new_folder_path)
                self.model.setRootPath('')
                self.model.setRootPath(rootPath)

    def createRootFile(self):
        new_file_name, ok = QInputDialog.getText(self, "Создание файла в корневой директории", "Введите имя файла:")
        if ok and new_file_name:
            rootPath = self.model.rootPath()
            new_file_path = os.path.join(rootPath, new_file_name)
            open(new_file_path, 'a').close()
            logging.info(f"Создан root файла: {new_file_path}")
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)

    def createFolderItem(self):
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        new_folder_name, ok = QInputDialog.getText(self, "Создание папки", "Введите имя папки:")
        if ok and new_folder_name:
            os.makedirs(os.path.join(filePath, new_folder_name))
            logging.info(f"Создана папка: {os.path.join(filePath, new_folder_name)}")
            rootPath = self.model.rootPath()
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)

    def createFileItem(self):
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        new_file_name, ok = QInputDialog.getText(self, "Создание файла", "Введите имя файла:")
        if ok and new_file_name:
            open(os.path.join(filePath, new_file_name), 'a').close()
            logging.info(f"Создан файл: {os.path.join(filePath, new_file_name)}")
            rootPath = self.model.rootPath()
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)

    def renameItem(self):
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        if filePath.endswith('/System') or filePath.endswith('/Корзина'):
            QMessageBox.warning(self, 'Ошибка', 'Эту папку нельзя переименовать!')
            logging.warning(f"Ошибка при переименование защищеной папки: {filePath}")
            return

        new_name, ok = QInputDialog.getText(self, "Переименование", "Введите новое имя:")
        if ok and new_name:
            os.rename(filePath, os.path.join(os.path.dirname(filePath), new_name))
            rootPath = self.model.rootPath()
            logging.info(f"Переименование объекта: {filePath} to {new_name}")
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)

    def deleteItem(self):
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        if filePath.endswith('/System') or filePath.endswith('/Корзина'):
            QMessageBox.warning(self, 'Ошибка', 'Эту папку нельзя удалить!')
            logging.warning(f"Ошибка удаление защищенного объекта: {filePath}")
            return

        trash_path = os.path.join('/home/dan/Superapp', 'Корзина')
        trash_file_path = os.path.join(trash_path, os.path.basename(filePath))

        self.original_paths[trash_file_path] = filePath

        os.rename(filePath, trash_file_path)
        logging.info(f"Перемещение объекта в корзину: {filePath} to {trash_file_path}")
        rootPath = self.model.rootPath()
        self.model.setRootPath('')
        self.model.setRootPath(rootPath)

    def deleteImmediatelyItem(self):
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        if filePath.endswith('/System') or filePath.endswith('/Корзина'):
            QMessageBox.warning(self, 'Ошибка', 'Эту папку нельзя удалить!')
            logging.warning(f"Ошбика быстрого удаления объекта: {filePath}")
            return

        if os.path.isfile(filePath) or os.path.islink(filePath):
            os.remove(filePath)
            logging.info(f"Удален файл: {filePath}")
        elif os.path.isdir(filePath):
            shutil.rmtree(filePath)
            logging.info(f"Удалена папка: {filePath}")

        rootPath = self.model.rootPath()
        self.model.setRootPath('')
        self.model.setRootPath(rootPath)

    def restoreItem(self):
        index = self.tree.currentIndex()
        filePath = self.model.filePath(index)

        original_path = self.original_paths.get(filePath, None)
        if not original_path:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось определить исходный путь файла!')
            return

        new_name, ok = QInputDialog.getText(self, "Восстановление",
                                            "Введите новое имя (или оставьте пустым для оригинального имени):")
        if ok:
            if not new_name:
                new_name = os.path.basename(original_path)
            new_file_path = os.path.join(os.path.dirname(original_path), new_name)

            # Проверка на наличие файла по новому пути
            if os.path.exists(new_file_path):
                QMessageBox.warning(self, 'Ошибка', f'Файл с именем "{new_name}" уже существует!')
                return

            # Создание родительской директории, если она не существует
            parent_dir = os.path.dirname(new_file_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            os.rename(filePath, new_file_path)
            rootPath = self.model.rootPath()
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)

    def clearTrash(self):
        reply = QMessageBox.question(self, 'Очистить корзину',
                                     'Уверены ли вы, что хотите очистить корзину?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            trash_path = os.path.join('/home/dan/Superapp', 'Корзина')
            for filename in os.listdir(trash_path):
                file_path = os.path.join(trash_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                    logging.info(f"Удален файл из корзины: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    logging.info(f"Удалена папка из корзины: {file_path}")
            rootPath = self.model.rootPath()
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)
        else:
            return

    def searchItem(self):
        search_text = self.searchInput.text().strip()
        if not search_text:
            rootPath = self.model.rootPath()
            self.model.setRootPath('')
            self.model.setRootPath(rootPath)
            logging.info("Создание результатов поиска")
            return

        matches = self.findItems(search_text, Qt.MatchContains | Qt.MatchRecursive, 0)

        if matches:
            first_match = matches[0]
            self.tree.setCurrentIndex(first_match)
            self.tree.scrollTo(first_match)
            logging.info(f"Поиск резултатов: {search_text}")
        else:
            QMessageBox.information(self, 'Поиск', f'Файл или папка с именем "{search_text}" не найдены.')
            logging.info(f"Ошибка нахождения объектов: {search_text}")

    def findItems(self, text, flags, column):
        matches = []
        stack = [self.model.index(0, 0, QModelIndex())]

        while stack:
            index = stack.pop()
            if index.isValid():
                text_data = self.model.data(index, Qt.DisplayRole)
                if text_data and text in text_data:
                    matches.append(index)

                if self.model.hasChildren(index):
                    for row in range(self.model.rowCount(index)):
                        stack.append(self.model.index(row, 0, index))

        return matches

    def copyItem(self):
        self.clipboard_path = self.model.filePath(self.tree.currentIndex())
        self.original_paths = {self.clipboard_path: None}
        logging.info(f"Скопирован объект: {self.clipboard_path}")

    def pasteItem(self):
        if not self.clipboard_path:
            return
        destination_path = self.model.filePath(self.tree.currentIndex())
        if not destination_path or not os.path.isdir(destination_path):
            QMessageBox.warning(self, 'Ошибка', 'Выберите папку для вставки!')
            logging.warning("Операция вставка прервана: destination not selected or not a folder")
            return
        if os.path.isfile(self.clipboard_path):
            destination = os.path.join(destination_path, os.path.basename(self.clipboard_path))
            shutil.copy2(self.clipboard_path, destination)
            logging.info(f"Вставлен файл: {self.clipboard_path} to {destination}")
        else:
            destination = os.path.join(destination_path, os.path.basename(self.clipboard_path))
            self.original_paths = {os.path.join(self.clipboard_path, f): os.path.join(destination, f) for f in os.listdir(self.clipboard_path)}
            shutil.copytree(self.clipboard_path, destination)
            logging.info(f"Вставлена папка: {self.clipboard_path} to {destination}")
        self.model.setRootPath('')
        self.model.setRootPath('/home/dan/Superapp')

        #####

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if self.is_system_folder(url.toLocalFile()):
                    event.ignore()
                    logging.info(f"Проигнорировн drag-enter: {url.toLocalFile()}")
                    return
            logging.info(f"Подтвержден drag-enter: {url.toLocalFile()}")
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if self.is_system_folder(url.toLocalFile()):
                    event.ignore()
                    logging.info(f"Проигнорирован drag-move event: {url.toLocalFile()}")
                    return
            event.acceptProposedAction()

    def dropEvent(self, event):
        destination_index = self.tree.indexAt(event.pos())
        destination_folder = self.model.filePath(destination_index)

        if not os.path.exists(destination_folder):
            destination_folder = self.get_destination_folder(event.pos())

        # Получаем список URL-адресов из MIME данных
        urls = event.mimeData().urls()

        for url in urls:
            file_path = url.toLocalFile()
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(destination_folder, file_name)

            # Перемещаем или копируем файл в зависимости от настроек
            if os.path.isfile(file_path):
                if os.path.exists(destination_path):
                    reply = QMessageBox.question(self, 'Перезапись файла',
                                                 f'Файл {file_name} уже существует в папке назначения. Заменить?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        shutil.copy2(file_path, destination_path)
                else:
                    shutil.copy2(file_path, destination_path)
            elif os.path.isdir(file_path):
                try:
                    shutil.copytree(file_path, destination_path)
                except FileExistsError:
                    reply = QMessageBox.question(self, 'Перезапись папки',
                                                 f'Папка {file_name} уже существует в папке назначения. Заменить?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        shutil.rmtree(destination_path)
                        shutil.copytree(file_path, destination_path)

        # После обработки каждого файла, обновляем виджет
        self.model.setRootPath('')
        self.model.setRootPath(destination_folder)

        event.acceptProposedAction()
    def is_system_folder(self, folder_path):
        system_folders = ["System", "Корзина"]
        folder_name = os.path.basename(folder_path)
        return folder_name in system_folders
        logging.info(f"Checked if system folder: {folder_path} - {is_system}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if self.is_system_folder(url.toLocalFile()):
                    event.ignore()
                    return
                print(url.toLocalFile())
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if self.is_system_folder(url.toLocalFile()):
                    event.ignore()
                    return
                # print(url.toLocalFile())
                if os.path.isdir(url.toLocalFile()):
                    self.target_directory = url.toLocalFile()
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                print(file_path)

    def get_destination_folder(self, position):
        destination_index = self.tree.indexAt(position)
        destination_folder = self.model.filePath(destination_index)
        return destination_folder
        logging.info(f"Determined destination folder: {destination_folder}")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Выход', 'Вы уверены, что хотите закрыть программу?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()