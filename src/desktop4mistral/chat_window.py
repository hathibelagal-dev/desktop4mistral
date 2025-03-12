from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QTextEdit, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMainWindow, QMenu
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QFontDatabase, QFont, QAction
from .__init__ import __app_title__
from .mistral.client import Client
from datetime import datetime

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
        self.chatContents = []
        self.firstSystemMessage()

    def firstSystemMessage(self):
        self.set_model("mistral-tiny", None)

    def initFonts(self):
        font_id = QFontDatabase.addApplicationFont(
            pkg_resources.resource_filename(
                "desktop4mistral", "fonts/FiraCode-VariableFont_wght.ttf"
            )
        )
        if font_id == -1:
            print("Failed to load font. Falling back to default.")
            self.fontFamily = "courier"
        else:
            self.fontFamily = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Loaded font: {self.fontFamily}")

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
        self.modelActions = []
        for model in self.mistralClient.listModels():
            model_action = QAction(model, self)
            model_action.setCheckable(True)
            model_action.setChecked(model == self.mistralClient.model_id)
            model_action.triggered.connect(
                lambda _, m=model, a=model_action: self.set_model(m, a)
            )
            self.modelActions.append(model_action)
            models_menu.addAction(model_action)

    def set_model(self, model, _):
        self.mistralClient.setModel(model)
        print("Switched to " + model)
        for m in self.modelActions:
            m.setChecked(m.text() == model)
        for item in self.mistralClient.model_data:
            if item["id"] == model:
                system_message = "Now using " + item["id"] + "\n"
                system_message += item["description"]
                if item["default_model_temperature"]:
                    system_message += "\nTemperature: " + str(item["default_model_temperature"])
                if item["max_context_length"]:
                    system_message += "\nMax Context Length: " + str(item["max_context_length"])
                if item["created"]:
                    date_created = datetime.fromtimestamp(item["created"])
                    system_message += "\Model creation date: " + date_created.strftime("%Y-%m-%d") + "\n"
                self.addSystemMessage(system_message)
                break

    def new_chat(self):
        self.chatDisplay.setRowCount(0)
        self.inputField.clear()
        self.scrollToBottom()

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

        self.chatDisplay = QTableWidget()
        self.chatDisplay.setColumnCount(2)
        self.chatDisplay.horizontalHeader().setVisible(False)
        self.chatDisplay.setEditTriggers(QTableWidget.NoEditTriggers)
        self.chatDisplay.horizontalHeader().setStretchLastSection(True)
        self.chatDisplay.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.chatDisplay.verticalHeader().setVisible(False)
        self.chatDisplay.setShowGrid(False)
        self.chatDisplay.setWordWrap(True)
        self.chatDisplay.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-family: "%s", sans-serif;
                font-size: 16px;
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
        """%self.fontFamily)
        layout.addWidget(self.chatDisplay)

        layout.addWidget(self.chatDisplay, stretch=1)

        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.inputField = QTextEdit()
        self.inputField.setPlaceholderText("Type your message here (Ctrl+Enter to send)...")
        self.inputField.setFixedHeight(60)
        self.inputField.setStyleSheet("""
            QTextEdit {
                background-color: #353535;
                color: #e0e0e0;
                border: 1px solid #454545;
                border-radius: 6px;
                padding: 8px;
                font-family: "%s", sans-serif;                                       
                font-size: 16px;
            }
            QTextEdit:focus {
                border: 1px solid #00b4ff;
                background-color: #3a3a3a;
            }
        """%self.fontFamily)
        input_layout.addWidget(self.inputField, stretch=1)

        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #00b4ff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: "%s", sans-serif;                                       
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #00c4ff;
            }
            QPushButton:pressed {
                background-color: #0098d4;
            }
        """%self.fontFamily)
        send_button.clicked.connect(self.sendMessage)
        input_layout.addWidget(send_button)

        layout.addWidget(input_widget)

        self.inputField.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.inputField and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and (event.modifiers() & Qt.ControlModifier):
                self.sendMessage()
                return True
        return super().eventFilter(obj, event)
    
    def scrollToBottom(self):
        scrollbar = self.chatDisplay.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def addUserMessage(self, user_message):
        self.chatContents.append({"role": "user", "content": user_message})

    def addAssistantMessage(self, assistant_message):
        self.chatContents.append({"role": "assistant", "content": assistant_message})

    def addSystemMessage(self, system_message):
        row_count = self.chatDisplay.rowCount()
        self.chatDisplay.insertRow(row_count)
        sender_item = QTableWidgetItem("System")
        sender_item.setForeground(QColor("#ffb0b0"))
        sender_item.setTextAlignment(Qt.AlignTop)
        message_item = QTableWidgetItem(system_message)
        message_item.setTextAlignment(Qt.AlignTop)
        message_item.setForeground(QColor("#e0e0e0"))
        self.chatDisplay.setItem(row_count, 0, sender_item)
        self.chatDisplay.setItem(row_count, 1, message_item)
        self.chatDisplay.resizeRowToContents(row_count)
        self.chatDisplay.scrollToBottom()


    def sendMessage(self):
        user_message = self.inputField.toPlainText().strip()
        if not user_message:
            return        
        self.addUserMessage(user_message)
        self.inputField.clear()        
        self.inputField.setText("Waiting for response...")
        self.inputField.setEnabled(False)
        row_count = self.chatDisplay.rowCount()
        self.chatDisplay.insertRow(row_count)
        sender_item = QTableWidgetItem("You")
        sender_item.setTextAlignment(Qt.AlignTop)
        sender_item.setForeground(QColor("#b0b0ff"))
        message_item = QTableWidgetItem(user_message)
        message_item.setForeground(QColor("#e0e0e0"))
        message_item.setTextAlignment(Qt.AlignTop)
        self.chatDisplay.setItem(row_count, 0, sender_item)
        self.chatDisplay.setItem(row_count, 1, message_item)
        self.chatDisplay.resizeRowToContents(row_count)

        llm_response = self.getLLMResponse()
        self.addAssistantMessage(llm_response)
        
        row_count = self.chatDisplay.rowCount()
        self.chatDisplay.insertRow(row_count)
        sender_item = QTableWidgetItem(self.mistralClient.model_id)
        sender_item.setTextAlignment(Qt.AlignTop)
        sender_item.setForeground(QColor("#ffb080"))        
        response_item = QTableWidgetItem(llm_response + "\n")
        response_item.setForeground(QColor("#e0e0e0"))
        response_item.setTextAlignment(Qt.AlignTop)
        
        self.chatDisplay.setItem(row_count, 0, sender_item)
        self.chatDisplay.setItem(row_count, 1, response_item)
        self.chatDisplay.resizeRowToContents(row_count)
        self.chatDisplay.scrollToBottom()
        self.inputField.clear()
        self.inputField.setEnabled(True)
        self.inputField.setFocus()

    def getLLMResponse(self):
        return self.mistralClient.sendChatMessage(self.chatContents)