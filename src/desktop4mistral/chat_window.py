from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QTextEdit, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMainWindow, QMenu
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QFontDatabase, QFont, QAction
from .__init__ import __app_title__
from .mistral.client import Client
import pkg_resources

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mistralClient = Client()
        self.setWindowTitle(__app_title__)
        self.setGeometry(100, 100, 1280, 720)
        self.initFonts()        
        self.initUI()
        self.initMenu()

    def initFonts(self):
        font_id = QFontDatabase.addApplicationFont(
            pkg_resources.resource_filename(
                "desktop4mistral", "fonts/FiraCode-VariableFont_wght.ttf"
            )
        )
        if font_id == -1:
            print("Failed to load font. Falling back to default.")
            self.font_family = "courier"
        else:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Loaded font: {self.font_family}")

    def initMenu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_action)
        file_menu.addSeparator()  
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)        
        file_menu.addAction(exit_action)

        models_menu = menu_bar.addMenu("Models")
        for model in self.mistralClient.listModels():
            model_action = QAction(model, self)
            model_action.triggered.connect(lambda _, model=model: self.mistralClient.setModel(model))
            models_menu.addAction(model_action)

    def new_chat(self):
        self.chat_display.setRowCount(0)
        self.input_field.clear()
        self.scroll_to_bottom()

    def initUI(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background-color: #212121;
            }
        """)

        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.chat_display = QTableWidget()
        self.chat_display.setColumnCount(2)
        self.chat_display.horizontalHeader().setVisible(False)
        self.chat_display.setEditTriggers(QTableWidget.NoEditTriggers)
        self.chat_display.horizontalHeader().setStretchLastSection(True)
        self.chat_display.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.chat_display.verticalHeader().setVisible(False)
        self.chat_display.setShowGrid(False)
        self.chat_display.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-family: "%s", sans-serif;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: none;
                padding: 5px;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """%self.font_family)
        layout.addWidget(self.chat_display)

        layout.addWidget(self.chat_display, stretch=1)

        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type your message here (Ctrl+Enter to send)...")
        self.input_field.setFixedHeight(60)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #353535;
                color: #e0e0e0;
                border: 1px solid #454545;
                border-radius: 6px;
                padding: 8px;
                font-family: "%s", sans-serif;                                       
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 1px solid #00b4ff;
                background-color: #3a3a3a;
            }
        """%self.font_family)
        input_layout.addWidget(self.input_field, stretch=1)

        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #00b4ff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: "%s", sans-serif;                                       
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #00c4ff;
            }
            QPushButton:pressed {
                background-color: #0098d4;
            }
        """%self.font_family)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        layout.addWidget(input_widget)

        self.input_field.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and (event.modifiers() & Qt.ControlModifier):
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def scroll_to_bottom(self):
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        user_message = self.input_field.toPlainText().strip()
        if not user_message:
            return
        
        row_count = self.chat_display.rowCount()
        self.chat_display.insertRow(row_count)
        sender_item = QTableWidgetItem("You")
        sender_item.setForeground(QColor("#b0b0ff"))
        message_item = QTableWidgetItem(user_message)
        message_item.setForeground(QColor("#e0e0e0"))
        self.chat_display.setItem(row_count, 0, sender_item)
        self.chat_display.setItem(row_count, 1, message_item)

        llm_response = self.get_llm_response(user_message)
        row_count = self.chat_display.rowCount()
        self.chat_display.insertRow(row_count)
        sender_item = QTableWidgetItem(self.mistralClient.model_id)
        sender_item.setForeground(QColor("#ffb080"))
        response_item = QTableWidgetItem(llm_response)
        response_item.setForeground(QColor("#e0e0e0"))
        self.chat_display.setItem(row_count, 0, sender_item)
        self.chat_display.setItem(row_count, 1, response_item)
        self.chat_display.scrollToBottom()
        self.input_field.clear()


    def get_llm_response(self, user_message):
        return "OK"