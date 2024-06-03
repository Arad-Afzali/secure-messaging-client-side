# client_gui.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton

class ChatClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('P2P Chat Client')
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        self.serverIpInput = QLineEdit(self)
        self.serverIpInput.setPlaceholderText('Server IP')
        layout.addWidget(self.serverIpInput)
        
        self.serverPortInput = QLineEdit(self)
        self.serverPortInput.setPlaceholderText('Server Port')
        layout.addWidget(self.serverPortInput)
        
        self.chatWindow = QTextEdit(self)
        self.chatWindow.setReadOnly(True)
        layout.addWidget(self.chatWindow)
        
        self.messageInput = QLineEdit(self)
        self.messageInput.setPlaceholderText('Enter message...')
        layout.addWidget(self.messageInput)
        
        self.sendButton = QPushButton('Send', self)  # Use self.sendButton
        self.sendButton.clicked.connect(self.sendMessage)
        layout.addWidget(self.sendButton)
        
        self.setLayout(layout)

    def sendMessage(self):
        message = self.messageInput.text()
        if message:
            self.chatWindow.append(f"You: {message}")
            self.messageInput.clear()
            # Here should be the logic to send the message to the server
