import sys
from PySide6.QtWidgets import QApplication
from .chat_window import ChatWindow

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
