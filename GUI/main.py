import sys
from PySide6.QtWidgets import QApplication
from front_page import MainWindow  # Changed to match the class name

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == '__main__':
    main()