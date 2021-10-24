#!/usr/bin/env python3

import socket
import random, string

def gen_rand_session_id(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for _ in range(length))

HOST = "127.0.0.1"
PORT = 3333

RFAP_VERSION = (1).to_bytes(2, 'big')

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(RFAP_VERSION)
    packet_type = (0).to_bytes(4, 'big')
    s.send(packet_type)
    session_id = gen_rand_session_id(32).encode("ascii")
    s.send(session_id)
    message_id = gen_rand_session_id(16).encode("ascii")
    s.send(message_id)
    header = "rug oiwergiowhe rigu weiurgh iwerg"
    while True:
        if len(header) == 0:
            s.send(b":end")
            break
        if len(header) < 4:
            header += " "
            continue
        s.send(header[:4].encode("utf-8"))
        header = header[4:]
    body = "this is my message"
    body_length = len(body).to_bytes(16, "big")
    s.send(body_length)
    header_checksum = session_id
    s.send(header_checksum)
    s.send(body.encode("utf-8"))
    s.send(b":end")
    body_checksum = session_id
    s.send(body_checksum)
    resp = s.recv(1024)
    print(resp)
    s.close()

