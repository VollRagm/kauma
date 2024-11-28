from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import helper

XOR_VALUE = 0xc0ffeec0ffeec0ffeec0ffeec0ffee11.to_bytes(16, byteorder='big')

def encrypt(key: bytes, data: bytes):

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    return helper.xor_buf(ciphertext, XOR_VALUE)


def decrypt(key: bytes, data: bytes):
    
    data = helper.xor_buf(data, XOR_VALUE)

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(data) + decryptor.finalize()
    return plaintext


def exec_cipher(assignment):

    arguments = assignment["arguments"]
    mode = arguments["mode"]
    key = helper.base64_to_buffer(arguments["key"])
    input = helper.base64_to_buffer(arguments["input"])

    if mode == "encrypt":
        return {"output": helper.buffer_to_base64(encrypt(key, input))}
    elif mode == "decrypt":
        return {"output": helper.buffer_to_base64(decrypt(key, input))}
