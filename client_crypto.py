# client_crypto.py
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

class CryptoManager:
    def __init__(self):
        self.rsa_key = RSA.generate(2048)
        self.aes_key = None

    def get_public_key(self):
        return self.rsa_key.publickey().export_key()

    def decrypt_aes_key(self, encrypted_key):
        cipher_rsa = PKCS1_OAEP.new(self.rsa_key)
        self.aes_key = cipher_rsa.decrypt(b64decode(encrypted_key))

    def encrypt_message(self, message):
        cipher_aes = AES.new(self.aes_key, AES.MODE_EAX)
        nonce = cipher_aes.nonce
        ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode())
        return b64encode(nonce + tag + ciphertext).decode()

    def decrypt_message(self, encrypted_message):
        data = b64decode(encrypted_message)
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        cipher_aes = AES.new(self.aes_key, AES.MODE_EAX, nonce=nonce)
        message = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return message.decode()
