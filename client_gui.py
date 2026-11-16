import html

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
                             QLineEdit, QPushButton, QTextEdit, QLabel)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFontDatabase

STATUS_COLORS = {
    "Connected": "#2e7d32",
    "Connecting": "#1565c0",
    "Disconnected": "#c62828",
}


class ChatClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.set_state("Disconnected")

    def init_ui(self):
        self.setWindowTitle("Secure Chat")
        self.resize(480, 640)
        self.setMinimumSize(400, 520)

        # Connection settings
        self.serverIpInput = QLineEdit()
        self.serverIpInput.setPlaceholderText("e.g. 127.0.0.1")
        self.serverPortInput = QLineEdit()
        self.serverPortInput.setPlaceholderText("e.g. 7004")
        self.certInput = QLineEdit()
        self.certInput.setPlaceholderText("server.crt (empty = no TLS)")

        self.connectButton = QPushButton("Connect")
        self.disconnectButton = QPushButton("Disconnect")
        buttons = QHBoxLayout()
        buttons.addWidget(self.connectButton)
        buttons.addWidget(self.disconnectButton)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.addRow("Server:", self.serverIpInput)
        form.addRow("Port:", self.serverPortInput)
        form.addRow("Certificate:", self.certInput)
        form.addRow(buttons)

        connectionBox = QGroupBox("Connection")
        connectionBox.setLayout(form)

        # Status and safety code
        self.connectionStatus = QLabel()
        self.connectionStatus.setAlignment(Qt.AlignCenter)
        self.connectionStatus.setFixedWidth(120)

        mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        mono.setPointSize(mono.pointSize() + 1)
        self.fingerprintLabel = QLabel("-")
        self.fingerprintLabel.setFont(mono)
        self.fingerprintLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.fingerprintLabel.setToolTip("Compare this code with your friend. "
                                         "If it is different, someone is in the middle.")

        statusRow = QHBoxLayout()
        statusRow.addWidget(self.connectionStatus)
        statusRow.addSpacing(8)
        statusRow.addWidget(QLabel("Safety code:"))
        statusRow.addWidget(self.fingerprintLabel, 1)

        # Chat
        self.chatWindow = QTextEdit()
        self.chatWindow.setReadOnly(True)
        self.messageInput = QLineEdit()
        self.messageInput.setPlaceholderText("Type a message and press Enter")
        self.sendButton = QPushButton("Send")
        inputRow = QHBoxLayout()
        inputRow.addWidget(self.messageInput, 1)
        inputRow.addWidget(self.sendButton)

        layout = QVBoxLayout()
        layout.addWidget(connectionBox)
        layout.addLayout(statusRow)
        layout.addWidget(self.chatWindow, 1)
        layout.addLayout(inputRow)
        self.setLayout(layout)

    # These slots are called from the network thread with QMetaObject.invokeMethod,
    # because Qt widgets may only be changed from the GUI thread.

    @pyqtSlot(str)
    def append_message(self, message):
        # Messages from the program itself, in grey
        self.chatWindow.append(f'<span style="color:#888;"><i>{html.escape(message)}</i></span>')

    @pyqtSlot(str, str)
    def append_chat(self, sender, message):
        color = "#42a5f5" if sender == "You" else "#66bb6a"
        self.chatWindow.append(f'<b style="color:{color};">{sender}:</b> {html.escape(message)}')

    @pyqtSlot(str)
    def set_state(self, state):
        self.connectionStatus.setText(state)
        self.connectionStatus.setStyleSheet(
            f"background-color: {STATUS_COLORS.get(state, '#c62828')}; color: white;"
            "padding: 3px; border-radius: 10px; font-weight: bold;")

        connected = state == "Connected"
        self.connectButton.setEnabled(state == "Disconnected")
        self.disconnectButton.setEnabled(state != "Disconnected")
        for widget in (self.serverIpInput, self.serverPortInput, self.certInput):
            widget.setEnabled(state == "Disconnected")
        # You can only write once the keys are exchanged
        self.messageInput.setEnabled(connected)
        self.sendButton.setEnabled(connected)
        if connected:
            self.messageInput.setFocus()

    @pyqtSlot(str)
    def update_fingerprint(self, fingerprint):
        self.fingerprintLabel.setText(fingerprint or "-")
