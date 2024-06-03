# client.py
import socket
import threading
from PyQt5.QtWidgets import QApplication
from client_gui import ChatClientGUI
from client_crypto import CryptoManager
import sys

class ChatClient:
    def __init__(self):
        self.gui = ChatClientGUI()
        self.crypto_manager = CryptoManager()
        self.socket = None

    def start(self):
        self.gui.show()
        self.gui.sendButton.clicked.connect(self.handle_send_message)

    def connect_to_server(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, int(port)))

        # Send RSA public key
        self.socket.sendall(self.crypto_manager.get_public_key())

        # Receive encrypted AES key
        encrypted_aes_key = self.socket.recv(4096)
        self.crypto_manager.decrypt_aes_key(encrypted_aes_key)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def handle_send_message(self):
        message = self.gui.messageInput.text()
        if message:
            encrypted_message = self.crypto_manager.encrypt_message(message)
            self.socket.sendall(encrypted_message.encode())
            self.gui.chatWindow.append(f"You: {message}")
            self.gui.messageInput.clear()

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.socket.recv(4096).decode()
                message = self.crypto_manager.decrypt_message(encrypted_message)
                self.gui.chatWindow.append(f"Friend: {message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.start()
    sys.exit(app.exec_())
