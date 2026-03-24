# Send a length-prefixed message through the socket, avoiding short writes.
def send_message(sock, msg):
    data = msg.encode('utf-8')
    header = len(data).to_bytes(4, byteorder='big')
    sock.sendall(header + data)


# Receive a length-prefixed message from the socket, avoiding short reads.
def receive_message(sock):
    header = _recv_exact(sock, 4)
    length = int.from_bytes(header, byteorder='big')
    data = _recv_exact(sock, length)
    return data.decode('utf-8')


# Read exactly n bytes from the socket, looping until complete.
def _recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        buf += chunk
    return buf
