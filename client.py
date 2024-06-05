import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot, Qt, QMetaObject, Q_ARG

from client_gui import ChatClientGUI
from client_crypto import CryptoManager

class ChatClient:
    def __init__(self, gui, crypto_manager):
        self.gui = gui
        self.crypto_manager = crypto_manager
        self.sock = None
        self.connected = False

        self.gui.connectButton.clicked.connect(self.connect_to_server)
        self.gui.sendButton.clicked.connect(self.send_message)

    def connect_to_server(self):
        host = self.gui.serverIpInput.text()
        port = self.gui.serverPortInput.text()

        if not host or not port:
            self.append_message("Please enter a valid IP and port.")
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, int(port)))
            self.connected = True
            self.append_message("Connected to server...")
            self.append_message("waiting for your friend's connection...")
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
        except Exception as e:
            self.append_message(f"Failed to connect to server: {e}")

    def listen_for_messages(self):
        try:
            while self.connected:
                message = self.sock.recv(4096).decode('utf-8')
                if message.startswith("REQUEST_PUBLIC_KEY"):
                    self.send_public_key()
                elif message.startswith("PEER_PUBLIC_KEY"):
                    self.receive_peer_public_key(message)
                elif message.startswith("DISCONNECT"):
                    self.connected = False
                    self.append_message("Disconnected from server.")
                else:
                    self.receive_message(message)
        except Exception as e:
            self.connected = False
            self.append_message(f"Disconnected from server: {e}")

    def send_public_key(self):
        public_key = self.crypto_manager.get_public_key().decode('utf-8')
        self.sock.sendall(f"PUBLIC_KEY:{public_key}".encode('utf-8'))

    def receive_peer_public_key(self, message):
        peer_public_key = message.split(":", 1)[1]
        self.crypto_manager.set_peer_public_key(peer_public_key)
        self.append_message("Your friend is now connected.")

    def send_message(self):
        message = self.gui.messageInput.text()
        if message and self.crypto_manager.peer_public_key:
            encrypted_message = self.crypto_manager.encrypt_message(message)
            try:
                self.sock.sendall(encrypted_message.encode('utf-8'))
                self.gui.messageInput.clear()
                self.append_message(f"You: {message}")
            except Exception as e:
                self.append_message(f"Failed to send message: {e}")
                self.close_connection()
        else:
            self.append_message("No peer public key set or empty message.")

    def receive_message(self, message):
        try:
            decrypted_message = self.crypto_manager.decrypt_message(message)
            self.append_message(f"Peer: {decrypted_message}")
        except Exception as e:
            self.append_message(f"Failed to decrypt message: {e}")

    def close_connection(self):
        if self.connected:
            try:
                self.sock.sendall("DISCONNECT".encode('utf-8'))
            except Exception as e:
                self.append_message(f"Error sending disconnect message: {e}")
            finally:
                self.sock.close()
                self.connected = False

    def append_message(self, message):
        QMetaObject.invokeMethod(self.gui, "append_message", Qt.QueuedConnection, Q_ARG(str, message))

def main():
    app = QApplication(sys.argv)
    gui = ChatClientGUI()
    crypto_manager = CryptoManager()
    client = ChatClient(gui, crypto_manager)

    gui.closeEvent = lambda event: (client.close_connection(), event.accept())
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
