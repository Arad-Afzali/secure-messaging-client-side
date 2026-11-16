# client_crypto.py
#
# How the encryption works:
# - Each client has a long-term Ed25519 identity key, saved to identity_key.pem.
#   Its fingerprint is what the two users compare to make sure nobody
#   (including the server) is in the middle.
# - For every chat session each client makes a new X25519 key pair and signs
#   the public part with its identity key.
# - Both sides do X25519 to get a shared secret, then HKDF turns it into two
#   AES-256-GCM keys, one for each direction.
# - Every message has a counter, so old messages cannot be replayed.

import os
import json
import base64
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.exceptions import InvalidSignature

IDENTITY_FILE = "identity_key.pem"


def b64(data):
    return base64.b64encode(data).decode('utf-8')


def unb64(text):
    return base64.b64decode(text)


def raw_public(key):
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


class CryptoManager:
    def __init__(self, identity_file=IDENTITY_FILE):
        self.identity_key = self.load_or_create_identity(identity_file)
        self.reset_session()

    def load_or_create_identity(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return serialization.load_pem_private_key(f.read(), password=None)
        key = Ed25519PrivateKey.generate()
        with open(path, 'wb') as f:
            f.write(key.private_bytes(serialization.Encoding.PEM,
                                      serialization.PrivateFormat.PKCS8,
                                      serialization.NoEncryption()))
        os.chmod(path, 0o600)
        return key

    def reset_session(self):
        # New X25519 key for every session (forward secrecy)
        self.session_key = X25519PrivateKey.generate()
        self.peer_identity = None
        self.send_key = None
        self.recv_key = None
        self.send_counter = 0
        self.recv_counter = 0

    def is_ready(self):
        return self.send_key is not None

    def get_public_key(self):
        # Our identity key, our session key, and a signature over the session key
        session_public = raw_public(self.session_key.public_key())
        signature = self.identity_key.sign(session_public)
        return json.dumps({
            "identity": b64(raw_public(self.identity_key.public_key())),
            "session": b64(session_public),
            "signature": b64(signature),
        })

    def set_peer_public_key(self, public_key):
        data = json.loads(public_key)
        peer_identity = Ed25519PublicKey.from_public_bytes(unb64(data["identity"]))
        peer_session = unb64(data["session"])

        try:
            peer_identity.verify(unb64(data["signature"]), peer_session)
        except InvalidSignature:
            raise ValueError("Peer session key has a bad signature")

        shared = self.session_key.exchange(X25519PublicKey.from_public_bytes(peer_session))

        my_session = raw_public(self.session_key.public_key())
        keys = HKDF(algorithm=hashes.SHA256(), length=64,
                    salt=b"".join(sorted([my_session, peer_session])),
                    info=b"secure-chat v2").derive(shared)

        # Both sides must agree which half is which, so sort by session key
        if my_session < peer_session:
            self.send_key, self.recv_key = keys[:32], keys[32:]
        else:
            self.send_key, self.recv_key = keys[32:], keys[:32]

        self.peer_identity = raw_public(peer_identity)
        self.send_counter = 0
        self.recv_counter = 0

    def fingerprint(self):
        # Same code on both sides. If the two users read out the same code,
        # nobody swapped the keys.
        mine = raw_public(self.identity_key.public_key())
        digest = hashlib.sha256(b"".join(sorted([mine, self.peer_identity]))).hexdigest().upper()
        return " ".join(digest[i:i + 4] for i in range(0, 24, 4))

    def encrypt_message(self, message):
        if not self.is_ready():
            raise ValueError("Peer public key is not set")
        self.send_counter += 1
        nonce = os.urandom(12)
        counter = str(self.send_counter).encode('utf-8')
        ciphertext = AESGCM(self.send_key).encrypt(nonce, message.encode('utf-8'), counter)
        return json.dumps({"n": self.send_counter, "nonce": b64(nonce), "data": b64(ciphertext)})

    def decrypt_message(self, encrypted_message):
        data = json.loads(encrypted_message)
        counter = int(data["n"])
        if counter <= self.recv_counter:
            raise ValueError("Old or repeated message, ignored")
        # Raises an error if the message was changed on the way
        plaintext = AESGCM(self.recv_key).decrypt(unb64(data["nonce"]), unb64(data["data"]),
                                                  str(counter).encode('utf-8'))
        self.recv_counter = counter
        return plaintext.decode('utf-8')
