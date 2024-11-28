import padding_oracle.server_simulator as server_simulator
import padding_oracle.server_connection as server_connection
import helper

import threading
from _thread import *

# Generates a list of Q-Blocks, where only the byte at the given index is different
def generate_q_blocks(count, index, fill: bytes) -> list[bytes]:

    q_blocks = []
    for i in range(count):
        q_blocks.append(b'\x00' * index + bytes([i]) + fill)
    return q_blocks

# Returns a list of indices where the oracle response is 1
def get_candidates(oracle_response: bytes) -> list[int]:

    candidates = []
    for i in range(len(oracle_response)):
        if oracle_response[i] == 1:
            candidates.append(i)
    return candidates


def next_fill(plaintext: bytes, currentByteIndex: int) -> bytes:
    
        fill = b''

        # Fill is the final bytes of the next Q-Block
        # Calculated by XORing the now know plaintext with the padding that is expected by PKCS7
        # The goal is that for each of the last bytes it holds that plaintext[i] ^ fill[i] = currentByteIndex + 1
        # currentByteIndex also is the value that is expected by PKCS7 padding

        for i in range(currentByteIndex):
            fill += bytes([plaintext[i] ^ (currentByteIndex + 1)])
    
        return fill


def decrypt_single_block(ciphertext: bytes, previousBlock: bytes, server: server_connection.ServerConnection) -> bytes:

    server.set_ciphertext(ciphertext)

    currentFill = b''
    plaintext = b''

    for currentByteIndex in range(16):

        # Let the server know we're about to blast it with 256 Q-Blocks
        server.send_q_count(256)

        blocks_to_send = b''
        for q_block in generate_q_blocks(256, 15 - currentByteIndex, currentFill):
            blocks_to_send += q_block

        server.send_q_blocks(blocks_to_send)
        response = server.receive_response(256)
        candidates = get_candidates(response)
        
        # Two candidates found, check which one of them is the correct one
        if len(candidates) > 1 and currentByteIndex != 15:

            # Build a new block that inverts the 0x0 before the candidate to probe if it fails
            probe_q_block = b'\x00' * (15 - currentByteIndex - 1) + bytes([0xFF, candidates[0]]) + currentFill

            server.send_q_count(1)
            server.send_q_blocks(probe_q_block)
            response = server.receive_response(1)

            # If the padding still is correct, then candidate[0] is the actual one
            if response[0] == 1:
                candidate = candidates[0]
            else:
                candidate = candidates[1]
        else:
            candidate = candidates[0]

        # The next plaintext byte is the candidate XORed with the expected padding value
        plaintext_candidate = (candidate ^ (currentByteIndex + 1))
        plaintext = bytes([(plaintext_candidate)]) + plaintext

        # calculate the last padding bytes for the next Q-Block
        currentFill = next_fill(plaintext, currentByteIndex + 1)

    # zero to terminate the connection
    server.send_q_count(0)
    
    # XOR the plaintext with the IV/previous block to get the actual plaintext
    plaintext = helper.xor_buf(plaintext, previousBlock)

    return plaintext

def attack(ciphertext: bytes, iv: bytes, host: str, port: int) -> bytes:

    blocks = helper.slice_blocks_16(ciphertext)
    plaintext_blocks = []

    for i in range(0, len(blocks)):

        connection = server_connection.ServerConnection(host, port)
        connection.connect()

        if i == 0:
            # First block is decrypted with the IV
            plaintext = decrypt_single_block(blocks[i], iv, connection)
        else:
            plaintext = decrypt_single_block(blocks[i], blocks[i - 1], connection)
        plaintext_blocks.append(plaintext)

        

    return helper.merge_blocks_16(plaintext_blocks)

simulation_server_started = False

def start_simulation_server():
    global simulation_server_started
    if simulation_server_started:
        return
    server = server_simulator.ServerSimulator()
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()
    simulation_server_started = True

def exec_attack(assignment):

    arguments = assignment["arguments"]
    ciphertext = helper.base64_to_buffer(arguments["ciphertext"])
    iv = helper.base64_to_buffer(arguments["iv"])
    host = arguments["hostname"]
    port = arguments["port"]

    # If the "magic" port and host are used, start the simulation server
    if port == 42069 and host == "server_simulator":
        host = "127.0.0.1"
        start_simulation_server()

    return {"plaintext": helper.buffer_to_base64(attack(ciphertext, iv, host, port))}