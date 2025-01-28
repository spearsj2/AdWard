import sys
from PySide6.QtWidgets import QApplication
from frontPage import frontPage

def main():
    app = QApplication(sys.argv)
    window = FrontPage()
    window.show()
    return app.exec()

if __name__ == '__main__':
    main()