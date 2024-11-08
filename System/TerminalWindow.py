import logging
import os
import subprocess

from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QLineEdit, QPushButton, QTextEdit
)

logging.basicConfig(filename='super_app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class TerminalWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Терминал')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.terminalOutput = QTextEdit()
        self.terminalOutput.setReadOnly(True)
        layout.addWidget(self.terminalOutput)

        self.commandInput = QLineEdit()
        self.commandInput.setPlaceholderText("Введите команду")
        layout.addWidget(self.commandInput)

        self.runButton = QPushButton("Выполнить")
        layout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.executeCommand)

        self.setLayout(layout)

    def executeCommand(self):
        command = self.commandInput.text().strip()
        self.commandInput.clear()
        self.executeCommandInternal(command)

    def executeCommandInternal(self, command):
        output = ""
        parts = command.split()
        if not parts:
            return

        cmd, args = parts[0], parts[1:]

        if cmd == "ls":
            output = self.ls()
        elif cmd == "pwd":
            output = self.pwd()
        elif cmd == "cd":
            if args:
                output = self.cd(args[0])
            else:
                output = "cd: missing argument"
        elif cmd == "cat":
            if args:
                output = self.cat(args[0])
            else:
                output = "cat: missing argument"
        elif cmd == "touch":
            if args:
                output = self.touch(args[0])
            else:
                output = "touch: missing argument"
        elif cmd == "mkdir":
            if args:
                output = self.mkdir(args[0])
            else:
                output = "mkdir: missing argument"
        elif cmd == "rmdir":
            if args:
                output = self.rmdir(args[0])
            else:
                output = "rmdir: missing argument"
        elif cmd == "rm":
            if args:
                output = self.rm(args[0])
            else:
                output = "rm: missing argument"
        elif cmd == "ping":
            if args:
                output = self.ping(args[0])
            else:
                output = "ping: missing argument"
        elif cmd == "ifconfig":
            output = self.ifconfig()
        elif cmd == "help":
            output = self.help()
        elif cmd == "clear":
            output = self.clear()
        else:
            output = f"{cmd}: command not found"

        self.terminalOutput.append(output)

    def ls(self):
        import os
        return "\n".join(os.listdir('.'))

    def pwd(self):
        import os
        return os.getcwd()

    def cd(self, path):
        import os
        try:
            os.chdir(path)
            return ""
        except Exception as e:
            return str(e)

    def cat(self, filename):
        try:
            with open(filename, 'r') as f:
                return f.read()
        except Exception as e:
            return str(e)

    def touch(self, filename):
        import os
        try:
            with open(filename, 'a'):
                os.utime(filename, None)
            return ""
        except Exception as e:
            return str(e)

    def mkdir(self, dirname):
        import os
        try:
            os.mkdir(dirname)
            return ""
        except Exception as e:
            return str(e)

    def rmdir(self, dirname):
        import os
        try:
            os.rmdir(dirname)
            return ""
        except Exception as e:
            return str(e)

    def rm(self, filename):
        import os
        try:
            os.remove(filename)
            return ""
        except Exception as e:
            return str(e)

    def ping(self, hostname):
        import socket
        try:
            host_ip = socket.gethostbyname(hostname)
            return f"Ping to {hostname} [{host_ip}] successful"
        except Exception as e:
            return str(e)

    def ifconfig(self):
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return f"Hostname: {hostname}\nIP Address: {ip_address}"

    def clear(self):
        self.terminalOutput.clear()
        return ""

    def help(self):
        return (
            "Available commands:\n"
            "  ls         - List directory contents\n"
            "  pwd        - Print working directory\n"
            "  cd <path>  - Change directory\n"
            "  cat <file> - Concatenate and display file\n"
            "  touch <file> - Change file timestamps or create empty file\n"
            "  mkdir <dir> - Make directories\n"
            "  rmdir <dir> - Remove empty directories\n"
            "  rm <file>  - Remove file\n"
            "  ping <host> - Ping host\n"
            "  ifconfig  - Display network configuration\n"
            "  clear     - Clear the terminal\n"
            "  help      - Display this help message\n"
        )


