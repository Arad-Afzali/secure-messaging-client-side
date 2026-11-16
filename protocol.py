# protocol.py
#
# TCP is a stream, so one recv() can return half a message or two messages
# glued together. Every message is sent as a 4-byte length and then the text.

import struct

MAX_MESSAGE_SIZE = 64 * 1024


def send_msg(sock, text):
    data = text.encode('utf-8')
    sock.sendall(struct.pack('>I', len(data)) + data)


def recv_exact(sock, size):
    data = b''
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data


def recv_msg(sock):
    size = struct.unpack('>I', recv_exact(sock, 4))[0]
    if size > MAX_MESSAGE_SIZE:
        raise ConnectionError("Message too large")
    return recv_exact(sock, size).decode('utf-8')
