import socket

class ServerConnection:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        self.sock.connect((self.host, self.port))

    def set_ciphertext(self, ciphertext):
        self.sock.sendall(ciphertext)

    def send_q_count(self, count):
        self.sock.sendall(count.to_bytes(2, byteorder='little'))

    def send_q_blocks(self, block):
        self.sock.sendall(block)
    
    def receive_response(self, count):
        return self.sock.recv(count)
    
