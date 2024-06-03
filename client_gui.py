# client_gui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QInputDialog

class ChatClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Secure Chat Client")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.serverIpInput = QLineEdit(self)
        self.serverIpInput.setPlaceholderText("Server IP")
        self.layout.addWidget(self.serverIpInput)

        self.serverPortInput = QLineEdit(self)
        self.serverPortInput.setPlaceholderText("Server Port")
        self.layout.addWidget(self.serverPortInput)

        self.chatWindow = QTextEdit(self)
        self.chatWindow.setReadOnly(True)
        self.layout.addWidget(self.chatWindow)

        self.messageInput = QLineEdit(self)
        self.layout.addWidget(self.messageInput)

        self.sendButton = QPushButton("Send", self)
        self.layout.addWidget(self.sendButton)

        self.setLayout(self.layout)

    def append_message(self, message):
        self.chatWindow.append(message)
