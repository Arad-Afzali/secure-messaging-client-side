# client.py
import socket
import threading
import sys
from PyQt5.QtWidgets import QApplication
from client_gui import ChatClientGUI
from client_crypto import CryptoManager

class ChatClient:
    def __init__(self):
        self.gui = ChatClientGUI()
        self.crypto_manager = CryptoManager()
        self.socket = None

    def start(self):
        self.gui.show()
        self.gui.sendButton.clicked.connect(self.handle_send_message)
        self.gui.serverIpInput.returnPressed.connect(self.connect_to_server)
        self.gui.serverPortInput.returnPressed.connect(self.connect_to_server)

    def connect_to_server(self):
        ip = self.gui.serverIpInput.text()
        port = int(self.gui.serverPortInput.text())
        threading.Thread(target=self.establish_connection, args=(ip, port), daemon=True).start()

    def establish_connection(self, ip, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))

            # Send RSA public key
            public_key = self.crypto_manager.get_public_key()
            self.socket.sendall(public_key)
            print(f"Sent public key to server: {public_key[:30]}...")

            # Receive peer's public key
            peer_public_key = self.socket.recv(4096)
            print(f"Received public key from peer: {peer_public_key[:30]}...")
            self.crypto_manager.set_peer_public_key(peer_public_key)

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def handle_send_message(self):
        message = self.gui.messageInput.text()
        if message:
            encrypted_message = self.crypto_manager.encrypt_message(message)
            self.socket.sendall(encrypted_message.encode())
            print(f"Sent encrypted message: {encrypted_message[:30]}...")
            self.gui.append_message(f"You: {message}")
            self.gui.messageInput.clear()

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.socket.recv(4096).decode()
                print(f"Received encrypted message: {encrypted_message[:30]}...")
                message = self.crypto_manager.decrypt_message(encrypted_message)
                self.gui.append_message(f"Friend: {message}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.start()
    sys.exit(app.exec_())
