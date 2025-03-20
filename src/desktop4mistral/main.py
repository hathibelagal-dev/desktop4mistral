import sys
from PySide6.QtWidgets import QApplication
from .chat_window import ChatWindow
import os

def main():
    k = None
    sys.stderr = open("error_log.txt", "w")
    if not os.environ.get("MISTRAL_API_KEY"):
        k = input("Please enter your Mistral API key: ")
        if not k:
            print("No API key provided.")
            sys.exit(1)
        os.environ["MISTRAL_API_KEY"] = k

    try:
        app = QApplication(sys.argv)
        window = ChatWindow()
        window.show()
        sys.exit(app.exec())
    except:
        pass
    finally:
        sys.stderr.close()

if __name__ == "__main__":
    main()
