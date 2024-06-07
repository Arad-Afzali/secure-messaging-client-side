# Secure Chat Client

This is the client application for a secure chat system. It connects to a secure chat server, exchanges public keys for secure communication, and allows encrypted messaging between clients.

## Features

- Generates RSA keys for secure communication.
- Encrypts and decrypts messages using RSA and OAEP padding.
- Connects to the secure chat server and exchanges public keys with another client.
- GUI for connecting, sending, and receiving messages.

## Requirements

- Python 3.x
- PyQt5
- pycryptodome

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

### Note (Optional Steps)

4. **SSL/TLS Support (Optional but Recommended)**:
To enable SSL/TLS support, you need to wrap the socket with SSL/TLS. Uncomment the relevant sections in the ChatClient class and provide the path to your certificate file:

    ```bash
    # Uncomment here for SSL/TLS certificate---------------------

    # Wrap the socket with SSL/TLS
    # context = ssl.create_default_context()
    # context.verify_mode = ssl.CERT_REQUIRED
    # context.check_hostname = True 
    # context.load_verify_locations('path/to/fullchain.pem')

    # self.sock = context.wrap_socket(self.sock, server_hostname=host)

    # ------------------------------------------------------------
    ```
5. **Obtaining SSL/TLS Certificates Self-Signed Certificates (for testing purposes)**:

You can generate self-signed certificates using OpenSSL:
    
    ```bash
    # Generate a new RSA private key
    openssl genrsa -out client.key 4096

    # Generate a Certificate Signing Request (CSR)
    openssl req -new -key client.key -out client.csr

    # Generate a self-signed SSL certificate
    openssl x509 -req -days 365 -in client.csr -signkey client.key -out client.crt
    ```

6. **Obtaining Certificates from a Certificate Authority (CA)**:

For production, it is recommended to obtain certificates from a trusted CA. Services like Let's Encrypt offer free SSL/TLS certificates:

Follow the instructions on the Let's Encrypt website to obtain your certificate.
Use the obtained fullchain.pem and privkey.pem files in the SSL/TLS configuration.

## Usage

1. **Start the client application**:
    ```bash
    python3 client.py
    ```
2. **Enter the server IP or domain and port, then click "Connect".**

3. **Once connected, exchange messages securely with your peer.**



## Contributing
Contributions are welcome! Please open an issue or submit a pull request.