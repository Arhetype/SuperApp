import sys
from PyQt5.QtWidgets import QApplication
from SuperApp import SuperApp

def main():
    app = QApplication(sys.argv)
    super_app = SuperApp()
    super_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()