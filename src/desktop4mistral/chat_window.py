from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QTextBrowser,
    QPushButton,
)
from PySide6.QtCore import Qt, QEvent, Signal, QObject, QThread
from PySide6.QtGui import QFontDatabase, QAction, QTextCursor
from .__init__ import __app_title__
from .markdown_handler import MarkdownConverter
from .mistral.client import Client
from .commands import Commands
import pkg_resources
from .state import State
from .speaker import Speaker

class ResponseWorker(QObject):
    finished = Signal(str)
    
    def __init__(self, mistral_client, commands_handler, chat_contents):
        super().__init__()
        self.mistral_client = mistral_client
        self.commands_handler = commands_handler
        self.chat_contents = chat_contents        
        
    def process(self):
        response = self.commands_handler.handle_command(self.chat_contents)
        if response:
            self.finished.emit(response)
            return
        
        try:
            response = self.mistral_client.sendChatMessage(self.chat_contents)
            
            self.finished.emit(response)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")


class ChatWindow(QMainWindow):
    response_received = Signal(str)

    COLORS = {
        "USER": "#b0b0ff",
        "SYSTEM": "#ffb0b0",
        "ASSISTANT": "#ffb080",
        "TEXT": "#e0e0e0",
    }

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.mistralClient = Client()
        self.speaker = None
        self.commandsHandler = Commands()
        self.markdownConverter = MarkdownConverter()
        self.setWindowTitle(__app_title__)
        self.setGeometry(100, 100, 1280, 720)

        self.chatContents = [{
            "role": "system",
            "content": self.commandsHandler.system_prompt()
        }]
        self.initFonts()
        self.initUI()
        self.initMenu()

        # Connect signals
        self.response_received.connect(self.handleResponse)

        # Initialize with first system message
        self.set_model("mistral-large-latest", None)
        
        # Thread management
        self.thread = None
        self.worker = None
        self.isClosing = False

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
                lambda checked, m=model, a=model_action: self.set_model(m, a)
            )
            self.modelActions.append(model_action)
            models_menu.addAction(model_action)

    def set_model(self, model, _):
        """Set the current Mistral model"""
        self.mistralClient.setModel(model)
        print(f"Switched to {model}")

        for action in self.modelActions:
            action.setChecked(action.text() == model)

        for item in self.mistralClient.model_data:
            if item["id"] == model:
                system_message = f"Now using {item['id']}\n\n{item['description']}\n\n"
                if item["default_model_temperature"]:
                    system_message += f"- Temperature: {item['default_model_temperature']}\n"
                if item["max_context_length"]:
                    system_message += f"- Max Context Length: {item['max_context_length']}\n\n"
                system_message += "Ready."
                self.addSystemMessage(system_message)
                break

    def new_chat(self):
        """Clear the chat display and start a new conversation"""
        self.chatDisplay.clear()
        self.inputField.clear()
        self.chatContents = [{
            "role": "user",
            "content": self.commandsHandler.system_prompt()
        }]

    def initUI(self):
        """Initialize the user interface components"""
        # Main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("QWidget { background-color: #212121; }")
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Chat display area with QTextBrowser
        self.chatDisplay = QTextBrowser()
        self.chatDisplay.setOpenExternalLinks(True)
        self.chatDisplay.setStyleSheet(
            f"""
            QTextBrowser {{
                background-color: #1f1f1f;
                color: #e0e0e0;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-family: "{self.fontFamily}", courier;
                font-size: 16px;
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
            "Type your message here (Ctrl+Enter or Cmd+Enter to send)..."
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
                font-family: "{self.fontFamily}", courier;
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
                font-family: "{self.fontFamily}", courier;
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
        cursor = self.chatDisplay.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chatDisplay.setTextCursor(cursor)
        self.chatDisplay.ensureCursorVisible()

    first_message = True
    def addMessageToDisplay(self, sender, message, color):
        """Add a message to the chat display with appropriate formatting"""
        styles = """<style>
            pre {
                font-weight: bold;
                color: #1db56a;
            }
            code {
                font-weight: bold;
                color: #1fbf6f;
            }
            ul {
                type: square;
            }
        </style>"""
        message_html = f"""
        {styles if self.first_message else ''}        
        <div style="margin-bottom: 16px;">
            <span style="color: {color}; font-weight: bold;">{sender}</span>
            <div style="color: {self.COLORS['TEXT']};">
                {self.formatMessageContent(message)}
            </div>
        </div>
        """
        
        # Append to chat display
        cursor = self.chatDisplay.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chatDisplay.append(message_html)
        self.scrollToBottom()

    def formatMessageContent(self, message):
        converted_message = self.markdownConverter.convert(message)
        print(converted_message)
        return converted_message

    def addUserMessage(self, message):
        """Add a user message to the chat history and display"""
        self.chatContents.append({"role": "user", "content": message})
        self.addMessageToDisplay("You", message, self.COLORS["USER"])

    def addAssistantMessage(self, message):
        """Add an assistant message to the chat history and display"""
        self.chatContents.append({"role": "assistant", "content": message})
        formatted_message = self.removeHidden(message)
        if State.get_talk_mode():
            if not self.speaker:
                self.speaker = Speaker()
            self.speaker.speak(formatted_message)
        self.addMessageToDisplay(
            self.mistralClient.model_id, formatted_message, self.COLORS["ASSISTANT"]
        )

    def removeHidden(self, message):
        if self.commandsHandler.HIDDEN_IDENTIFIER_START in message:
            start_index = message.index(self.commandsHandler.HIDDEN_IDENTIFIER_START)
            end_index = message.index(self.commandsHandler.HIDDEN_IDENTIFIER_END)
            message = message[:start_index] + message[end_index + len(self.commandsHandler.HIDDEN_IDENTIFIER_END):]
        return message.strip()

    def addSystemMessage(self, message):
        """Add a system message to the display (not added to chat history)"""
        self.addMessageToDisplay("System", message, self.COLORS["SYSTEM"])

    def handleResponse(self, response):
        """Safely handle response from the worker thread"""
        if not self.isClosing:
            self.addAssistantMessage(response)
            self.inputField.clear()
            self.inputField.setEnabled(True)
            self.inputField.setFocus()

    def sendMessage(self):
        """Send the user message and get a response"""
        user_message = self.inputField.toPlainText().strip()
        if not user_message:
            return

        self.addUserMessage(user_message)

        self.inputField.clear()
        self.inputField.setText("Waiting for response...")
        self.inputField.setEnabled(False)

        self.cleanupThread()
        
        self.thread = QThread()
        self.worker = ResponseWorker(self.mistralClient, self.commandsHandler, self.chatContents)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.process)
        self.worker.finished.connect(self.handleResponse)
        self.worker.finished.connect(self.cleanupThread)
        
        self.thread.start()

    def cleanupThread(self):
        """Safely clean up thread and worker"""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
            
        # Reset references
        self.thread = None
        self.worker = None

    def closeEvent(self, event):
        """Handle window close event"""
        self.isClosing = True
        
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(1000)            
            if self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
                
        super().closeEvent(event)