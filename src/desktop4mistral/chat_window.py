from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
)
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QColor, QFontDatabase, QAction
from .__init__ import __app_title__
from .markdown_handler import MarkdownConverter
from .mistral.client import Client
from datetime import datetime
import pkg_resources
import threading


class ChatWindow(QMainWindow):
    # Define signals for thread-safe UI updates
    response_received = Signal(str)

    # Define color constants
    COLORS = {
        "USER": QColor("#b0b0ff"),
        "SYSTEM": QColor("#ffb0b0"),
        "ASSISTANT": QColor("#ffb080"),
        "TEXT": QColor("#e0e0e0"),
    }

    def __init__(self):
        super().__init__()
        self.mistralClient = Client()
        self.setWindowTitle(__app_title__)
        self.setGeometry(100, 100, 1280, 720)

        # Initialize UI components
        self.chatContents = []
        self.initFonts()
        self.initUI()
        self.initMenu()

        # Connect signals
        self.response_received.connect(self.updateAssistantResponse)

        # Initialize with first system message
        self.set_model("mistral-tiny", None)

    def initFonts(self):
        """Load custom font for the application"""
        font_path = pkg_resources.resource_filename(
            "desktop4mistral", "fonts/FiraCode-VariableFont_wght.ttf"
        )
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print("Failed to load font. Falling back to default.")
            self.fontFamily = "courier"
        else:
            self.fontFamily = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Loaded font: {self.fontFamily}")

    def initMenu(self):
        """Initialize the application menu bar"""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Models menu
        models_menu = menu_bar.addMenu("Models")
        self.modelActions = []

        for model in self.mistralClient.listModels():
            model_action = QAction(model, self)
            model_action.setCheckable(True)
            model_action.setChecked(model == self.mistralClient.model_id)
            model_action.triggered.connect(
                lambda checked, m=model, a=model_action: self.set_model(m, a)
            )
            self.modelActions.append(model_action)
            models_menu.addAction(model_action)

    def set_model(self, model, _):
        """Set the current Mistral model"""
        self.mistralClient.setModel(model)
        print(f"Switched to {model}")

        # Update menu checkboxes
        for action in self.modelActions:
            action.setChecked(action.text() == model)

        # Display model information as system message
        for item in self.mistralClient.model_data:
            if item["id"] == model:
                system_message = [f"Now using {item['id']}", item["description"]]

                if item["default_model_temperature"]:
                    system_message.append(
                        f"Temperature: {item['default_model_temperature']}"
                    )

                if item["max_context_length"]:
                    system_message.append(
                        f"Max Context Length: {item['max_context_length']}"
                    )

                if item["created"]:
                    date_created = datetime.fromtimestamp(item["created"])
                    system_message.append(
                        f"Model creation date: {date_created.strftime('%Y-%m-%d')}"
                    )

                system_message = "\n- ".join(system_message)
                self.addSystemMessage(system_message)
                break

    def new_chat(self):
        """Clear the chat display and start a new conversation"""
        self.chatDisplay.setRowCount(0)
        self.inputField.clear()
        self.chatContents = []
        self.scrollToBottom()

    def initUI(self):
        """Initialize the user interface components"""
        # Main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("QWidget { background-color: #212121; }")
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Chat display area
        self.chatDisplay = QTableWidget()
        self.chatDisplay.setColumnCount(2)
        self.chatDisplay.horizontalHeader().setVisible(False)
        self.chatDisplay.setEditTriggers(QTableWidget.NoEditTriggers)
        self.chatDisplay.horizontalHeader().setStretchLastSection(True)
        self.chatDisplay.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.chatDisplay.verticalHeader().setVisible(False)
        self.chatDisplay.setShowGrid(False)
        self.chatDisplay.setWordWrap(True)

        self.chatDisplay.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-family: "{self.fontFamily}", sans-serif;
                font-size: 16px;
            }}
            QHeaderView::section {{
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: none;
                padding: 5px;
            }}
            QScrollBar:vertical {{
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #4a4a4a;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        )
        layout.addWidget(self.chatDisplay, stretch=1)

        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.inputField = QTextEdit()
        self.inputField.setPlaceholderText(
            "Type your message here (Ctrl+Enter to send)..."
        )
        self.inputField.setFixedHeight(60)
        self.inputField.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: #353535;
                color: #e0e0e0;
                border: 1px solid #454545;
                border-radius: 6px;
                padding: 8px;
                font-family: "{self.fontFamily}", sans-serif;
                font-size: 16px;
            }}
            QTextEdit:focus {{
                border: 1px solid #00b4ff;
                background-color: #3a3a3a;
            }}
        """
        )

        input_layout.addWidget(self.inputField, stretch=1)

        send_button = QPushButton("Send")
        send_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #00b4ff;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: "{self.fontFamily}", sans-serif;
                font-size: 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #00c4ff;
            }}
            QPushButton:pressed {{
                background-color: #0098d4;
            }}
        """
        )

        send_button.clicked.connect(self.sendMessage)
        input_layout.addWidget(send_button)
        layout.addWidget(input_widget)

        # Install event filter for keyboard shortcuts
        self.inputField.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle keyboard events for the input field"""
        if obj == self.inputField and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and (
                event.modifiers() & Qt.ControlModifier
            ):
                self.sendMessage()
                return True
        return super().eventFilter(obj, event)

    def scrollToBottom(self):
        """Scroll the chat display to the bottom"""
        self.chatDisplay.scrollToBottom()

    def addMessageToDisplay(self, sender, message, color):
        """Add a message to the chat display with appropriate formatting"""
        row_count = self.chatDisplay.rowCount()
        self.chatDisplay.insertRow(row_count)

        # Create sender item
        sender_item = QTableWidgetItem(sender)
        sender_item.setTextAlignment(Qt.AlignTop)
        sender_item.setForeground(color)

        # Create message item
        message = message + "\n"
        message_item = QTableWidgetItem(message)
        message_item.setTextAlignment(Qt.AlignTop)
        message_item.setForeground(self.COLORS["TEXT"])

        # Add items to the table
        self.chatDisplay.setItem(row_count, 0, sender_item)
        self.chatDisplay.setItem(row_count, 1, message_item)

        # Resize row and scroll
        self.chatDisplay.resizeRowToContents(row_count)
        self.scrollToBottom()

    def addUserMessage(self, message):
        """Add a user message to the chat history and display"""
        self.chatContents.append({"role": "user", "content": message})
        self.addMessageToDisplay("You", message, self.COLORS["USER"])

    def addAssistantMessage(self, message):
        """Add an assistant message to the chat history and display"""
        self.chatContents.append({"role": "assistant", "content": message})
        self.addMessageToDisplay(
            self.mistralClient.model_id, message, self.COLORS["ASSISTANT"]
        )

    def addSystemMessage(self, message):
        """Add a system message to the display (not added to chat history)"""
        self.addMessageToDisplay("System", message, self.COLORS["SYSTEM"])

    def updateAssistantResponse(self, response):
        """Update UI with assistant response (called from the main thread)"""
        self.addAssistantMessage(response)
        self.inputField.clear()
        self.inputField.setEnabled(True)
        self.inputField.setFocus()

    def sendMessage(self):
        """Send the user message and get a response"""
        user_message = self.inputField.toPlainText().strip()
        if not user_message:
            return

        # Add user message to display
        self.addUserMessage(user_message)

        # Disable input while waiting for response
        self.inputField.clear()
        self.inputField.setText("Waiting for response...")
        self.inputField.setEnabled(False)

        # Get response in a separate thread
        threading.Thread(target=self.getResponseInBackground, daemon=True).start()

    def getResponseInBackground(self):
        """Get LLM response in a background thread to prevent UI freezing"""
        try:
            response = self.mistralClient.sendChatMessage(self.chatContents)
            self.response_received.emit(response)
        except Exception as e:
            self.response_received.emit(f"Error: {str(e)}")
        finally:
            self.inputField.setEnabled(True)
            self.inputField.setFocus()
