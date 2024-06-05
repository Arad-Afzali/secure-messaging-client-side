from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QProgressBar
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QTimer

class ChatClientGUI(QWidget):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.message_received.connect(self.append_message)

    def init_ui(self):
        self.setWindowTitle("Secure Chat Client")

        self.layout = QVBoxLayout()

        self.serverIpLabel = QLabel("Server IP:")
        self.serverIpInput = QLineEdit()
        self.serverPortLabel = QLabel("Server Port:")
        self.serverPortInput = QLineEdit()
        self.connectButton = QPushButton("Connect")
        self.disconnectButton = QPushButton("Disonnect")
        

        self.chatWindow = QTextEdit()
        self.chatWindow.setReadOnly(True)
        self.messageInput = QLineEdit()
        self.sendButton = QPushButton("Send")


        self.layout.addWidget(self.serverIpLabel)
        self.layout.addWidget(self.serverIpInput)
        self.layout.addWidget(self.serverPortLabel)
        self.layout.addWidget(self.serverPortInput)
        self.layout.addWidget(self.connectButton)
        self.layout.addWidget(self.disconnectButton)
        self.layout.addWidget(self.chatWindow)
        self.layout.addWidget(self.messageInput)
        self.layout.addWidget(self.sendButton)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def append_message(self, message):
        self.chatWindow.append(message)
