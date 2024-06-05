from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QProgressBar
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5 import QtCore


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

        # Connection status label
        self.connectionStatusLabel = QLabel("Connection Status:")
        self.connectionStatus = QLabel("Disconnected")
        self.update_connection_status("Disconnected")

        self.connectButton = QPushButton("Connect")
        self.disconnectButton = QPushButton("Disconnect")

        self.chatWindow = QTextEdit()
        self.chatWindow.setReadOnly(True)
        self.messageInput = QLineEdit()
        self.sendButton = QPushButton("Send")

        self.layout.addWidget(self.serverIpLabel)
        self.layout.addWidget(self.serverIpInput)
        self.layout.addWidget(self.serverPortLabel)
        self.layout.addWidget(self.serverPortInput)
        self.layout.addWidget(self.connectionStatusLabel)
        self.layout.addWidget(self.connectionStatus)
        self.layout.addWidget(self.connectButton)
        self.layout.addWidget(self.disconnectButton)
        self.layout.addWidget(self.chatWindow)
        self.layout.addWidget(self.messageInput)
        self.layout.addWidget(self.sendButton)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def append_message(self, message):
        self.chatWindow.append(message)

    def update_connection_status(self, status):
        base_style = "color: white; padding: 2px; border-radius: 10px;"
        if status == "Connected":
            self.connectionStatus.setText("Connected")
            self.connectionStatus.setStyleSheet("background-color: green; " + base_style)
            self.connectionStatus.setAlignment(QtCore.Qt.AlignCenter)

        elif status == "Connecting":
            self.connectionStatus.setText("Connecting")
            self.connectionStatus.setStyleSheet("background-color: blue; " + base_style)
            self.connectionStatus.setAlignment(QtCore.Qt.AlignCenter)

        else:
            self.connectionStatus.setText("Disconnected")
            self.connectionStatus.setStyleSheet("background-color: red; " + base_style)
            self.connectionStatus.setAlignment(QtCore.Qt.AlignCenter)

