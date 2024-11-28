from cryptography.hazmat.primitives import padding
import socket

import helper

# This is a simulator for the padding oracle server in order to test the padding oracle attack
# The server simulator uses XOR encryption

class ServerSimulator:
    def __init__(self, demo_key=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'):
        self.demo_key = demo_key
        self.initial_ciphertext = b''
        self.excepted_q_blocks = 0
        self.q_blocks = []

    # Simple encrypt with PKCS7 padding, fixed Key and IV
    def encrypt(self, plain):
        # Pad first
        unpadder = padding.PKCS7(128).padder()
        plain = unpadder.update(plain) + unpadder.finalize()
    
        blocks = helper.slice_blocks_16(plain)
        ciphertext = b''
        prev_block = b'\x00' * 16

        for block in blocks:
            # Do CBC
            block = helper.xor_buf(block, prev_block)

            # Cipher is a simple XOR for demonstration
            block = helper.xor_buf(block, self.demo_key)
            prev_block = block
            ciphertext += block

        return ciphertext

    def create_padding_oracle_response(self):
        response = b''

        # Try to decrypt the ciphertext with all Q-Blocks
        for q_block in self.q_blocks:
            # Decrypt the block
            plain = helper.xor_buf(self.initial_ciphertext, self.demo_key)

            # Do CBC
            plain = helper.xor_buf(plain, q_block)

            try:
                unpadder = padding.PKCS7(128).unpadder()
                unpadder.update(plain)
                unpadder.finalize()
            except ValueError:
                response += b'\x00'  # Padding is invalid
            else:
                response += b'\x01'

        return response

    # Appends a new Q-Block and returns the padding oracle response on the last block
    def add_q_block(self, block):
        self.q_blocks.append(block)
        self.excepted_q_blocks -= 1

        if self.excepted_q_blocks == 0:
            # Send the last block to the server
            response = self.create_padding_oracle_response()
            self.q_blocks.clear()
            return response

    def start_server(self, host='127.0.0.1', port=42069):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen(1)
            #print(f"Server listening on {host}:{port}")

            while True:
                conn, addr = server_socket.accept()
                with conn:
                    #print("Connected " + str(addr))
                    self.initial_ciphertext = conn.recv(16)

                    while True:
                        q_count_data = conn.recv(2)
                        self.excepted_q_blocks = int.from_bytes(q_count_data, byteorder='little')

                        # Disconnect if zero blocks are expected
                        if self.excepted_q_blocks == 0:
                            break

                        total_bytes_expected = self.excepted_q_blocks * 16
                        bytes_received = conn.recv(total_bytes_expected)

                        for i in range(0, total_bytes_expected, 16):
                            q_block = bytes_received[i:i + 16]
                            response = self.add_q_block(q_block)
                            if response:
                                conn.sendall(response)