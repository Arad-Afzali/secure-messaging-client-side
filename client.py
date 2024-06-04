import socket
import threading
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMetaObject, Q_ARG, QTimer, Qt, pyqtSignal, QObject
from client_gui import ChatClientGUI
from client_crypto import CryptoManager
import errno


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
        self.gui.sendPublicKeyButton.clicked.connect(self.send_public_key)
        self.gui.receivePublicKeyButton.clicked.connect(self.receive_public_key)

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

        QTimer.singleShot(5000, self.send_public_key_signal.emit)
        QTimer.singleShot(25000, self.receive_public_key_signal.emit)

    def on_timer_timeout(self):
        self.time_elapsed += 1
        self.update_progress_signal.emit(self.time_elapsed)

    def update_progress_bar(self, elapsed_time):
        self.gui.progressBar.setValue(int((elapsed_time / 30) * 100))

        if elapsed_time == 10:
            self.gui.sendPublicKeyButton.setEnabled(True)
        elif elapsed_time == 30:
            self.gui.receivePublicKeyButton.setEnabled(True)
            self.timer.stop()

    def send_public_key(self):
        if self.socket:
            public_key = self.crypto_manager.get_public_key()
            self.socket.sendall(b'KEY:' + public_key)
            print(f"Sent public key to server: {public_key[:30]}...")

    def receive_public_key(self):
        if self.socket:
            try:
                self.socket.settimeout(5)  # Set a timeout for receiving data
                self.socket.sendall(b'REQ_KEY')
                peer_public_key = self.socket.recv(4096)
                if peer_public_key:
                    self.crypto_manager.set_peer_public_key(peer_public_key)
                    print(f"Received public key from peer: {peer_public_key[:30]}...")
                else:
                    raise socket.timeout
            except socket.timeout:
                print("No public key received from the server within the timeout period.")
                self.notify_disconnection()
            except Exception as e:
                print(f"Error receiving public key: {e}")
            finally:
                if self.socket:
                    self.socket.settimeout(None)  # Remove the timeout only if the socket exists

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
            except OSError as e:
                if e.errno == errno.EWOULDBLOCK:
                    print("Resource temporarily unavailable; retrying...")
                    continue
                else:
                    print(f"Error receiving message: {e}")
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        self.close_connection()

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
