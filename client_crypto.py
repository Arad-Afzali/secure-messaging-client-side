# client_crypto.py
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

class CryptoManager:
    def __init__(self):
        self.private_key = RSA.generate(4096)
        self.public_key = self.private_key.publickey()
        self.peer_public_key = None

    def get_public_key(self):
        return self.public_key.export_key()

    def set_peer_public_key(self, public_key):
        self.peer_public_key = RSA.import_key(public_key)

    def encrypt_message(self, message):
        if self.peer_public_key is None:
            raise ValueError("Peer public key is not set")
        cipher_rsa = PKCS1_OAEP.new(self.peer_public_key)
        encrypted_message = cipher_rsa.encrypt(message.encode('utf-8'))
        encrypted_message_b64 = base64.b64encode(encrypted_message).decode('utf-8')
        return encrypted_message_b64

    def decrypt_message(self, encrypted_message_b64):
        try:
            encrypted_message = base64.b64decode(encrypted_message_b64)
            cipher_rsa = PKCS1_OAEP.new(self.private_key)
            decrypted_message = cipher_rsa.decrypt(encrypted_message).decode('utf-8')
            return decrypted_message
        except Exception as e:
            print(f"Error decrypting message: {e}")
            return ""
