# Secure Chat Client (end-to-end encryption)

This is the client application for a secure chat system. It connects to a secure chat server, exchanges public keys for secure communication, and allows encrypted messaging between clients.

![alt text](<ss.png>)

## Server Application

The server application is necessary for the connection of client apps. You can find the server application repository and instructions on how to set it up below:

https://github.com/Arad-Afzali/secure-messaging-server-side

Please follow the installation and usage instructions in the server application's README to ensure proper communication with the clients.

## Features

- **End-to-end encryption.** Messages are encrypted with AES-256-GCM. The keys come from an X25519 key exchange, run through HKDF-SHA256, with a separate key for each direction.
- **New keys every session.** Each chat uses a fresh X25519 key pair, so a key leaked later cannot decrypt old chats (forward secrecy).
- **Safety code.** Each client has a long-term Ed25519 identity key (`identity_key.pem`) and signs its session key with it. Both users see the same safety code; if they compare it (in person or by phone) and it matches, the server or anyone else cannot have swapped the keys.
- **Replay and tamper protection.** Every message carries a counter that is checked, and AES-GCM rejects any message changed on the way.
- **TLS to the server.** Give the client the server's certificate and the connection to the server is also wrapped in TLS, with the certificate and hostname checked.
- **Message framing.** Every message is sent with a 4-byte length first (`protocol.py`), so long messages and fast messages arrive whole.
- PyQt5 GUI for connecting, chatting and showing the safety code.

### How it works

1. Both clients connect to the server and send their identity key, a new X25519 session key, and a signature over the session key.
2. The server passes each client's keys to the other. It never sees a private key.
3. Each client checks the signature, does X25519, and derives the two AES keys.
4. Both users compare the safety code shown in the app.
5. Messages are encrypted on one client and only decrypted on the other. The server only forwards them.

## Requirements

- Python 3.8+
- PyQt5
- cryptography

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/Arad-Afzali/secure-messaging-client-side.git
    cd secure-messaging-client-side
    ```

2. **Create a virtual environment and activate it** (Recommended):

    **On macOS and Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

    **On Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

4. **TLS (recommended)**: get `server.crt` from whoever runs the server (see `make_cert.sh` in the server repository). It holds no secret.

## Usage

1. **Start the client application**:
    ```bash
    python3 client.py
    ```
2. **Enter the server IP or domain, the port and the path to `server.crt`, then click "Connect".** Without a certificate the app still works, but the connection to the server is not TLS.

3. **When your friend connects, compare the safety code.** Read it out over a phone call or check it in person. If the codes differ, disconnect: someone is in the middle.

4. **Chat.**



## Contributing
Contributions are welcome! Please open an issue or submit a pull request.
