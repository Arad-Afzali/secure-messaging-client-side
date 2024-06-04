import socket
import threading
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMetaObject, Q_ARG, QTimer, Qt, pyqtSignal, QObject
from client_gui import ChatClientGUI
from client_crypto import CryptoManager

class ChatClient(QObject):
    start_timer_signal = pyqtSignal()
    send_public_key_signal = pyqtSignal()
    receive_public_key_signal = pyqtSignal()
    update_progress_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.gui = ChatClientGUI()
        self.crypto_manager = CryptoManager()
        self.socket = None
        self.time_elapsed = 0

        self.start_timer_signal.connect(self.start_timer)
        self.send_public_key_signal.connect(self.send_public_key)
        self.receive_public_key_signal.connect(self.receive_public_key)
        self.update_progress_signal.connect(self.update_progress_bar)

        self.gui.closeEvent = self.close_event  # Ensure the server is notified when the client closes

    def start(self):
        self.gui.show()
        self.gui.sendButton.clicked.connect(self.handle_send_message)
        self.gui.connectButton.clicked.connect(self.connect_to_server)


    def connect_to_server(self):
        ip = self.gui.serverIpInput.text()
        port = int(self.gui.serverPortInput.text())
        threading.Thread(target=self.establish_connection, args=(ip, port), daemon=True).start()

    def establish_connection(self, ip, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.start_timer_signal.emit()
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def start_timer(self):
        self.gui.progressBar.setValue(0)
        self.time_elapsed = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)
        self.timer.start(1000)

        QTimer.singleShot(10000, self.send_public_key_signal.emit)
        QTimer.singleShot(30000, self.receive_public_key_signal.emit)

    def on_timer_timeout(self):
        self.time_elapsed += 1
        self.update_progress_signal.emit(self.time_elapsed)

    def update_progress_bar(self, elapsed_time):
        self.gui.progressBar.setValue(int((elapsed_time / 30) * 100))

    def send_public_key(self):
        if self.socket:
            public_key = self.crypto_manager.get_public_key()
            self.socket.sendall(b'KEY:' + public_key)
            print(f"Sent public key to server: {public_key[:30]}...")

    def receive_public_key(self):
        if self.socket:
            self.socket.sendall(b'REQ_KEY')
            peer_public_key = self.socket.recv(4096)
            self.crypto_manager.set_peer_public_key(peer_public_key)
            print(f"Received public key from peer: {peer_public_key[:30]}...")
            QMetaObject.invokeMethod(self.gui, "append_message", Q_ARG(str, "Connected!"))


    def handle_send_message(self):
        message = self.gui.messageInput.text()
        if message:
            try:
                encrypted_message = self.crypto_manager.encrypt_message(message)
                self.socket.sendall((encrypted_message + "\n").encode())
                print(f"Sent encrypted message: {encrypted_message[:30]}...")
                self.gui.append_message(f"You: {message}")
                self.gui.messageInput.clear()
            except Exception as e:
                print(f"Error sending message: {e}")

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    print("Connection closed by the server.")
                    break
                buffer += data.decode()
                while "\n" in buffer:
                    encrypted_message, buffer = buffer.split("\n", 1)
                    print(f"Received encrypted message: {encrypted_message[:30]}...")
                    message = self.crypto_manager.decrypt_message(encrypted_message)
                    QMetaObject.invokeMethod(self.gui, "append_message", Q_ARG(str, f"Friend: {message}"))
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        self.notify_disconnection()

    def notify_disconnection(self):
        self.close_connection()
        QMetaObject.invokeMethod(self.gui, "append_message", Q_ARG(str, "Disconnected from the server."))

    def close_connection(self):
        if self.socket:
            try:
                self.socket.close()
                print("Socket closed.")
            except Exception as e:
                print(f"Error closing socket: {e}")
            finally:
                self.socket = None

    def close_event(self, event):
        self.close_connection()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.start()
    sys.exit(app.exec_())