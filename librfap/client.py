#!/usr/bin/env python3

import sys
import socket
import yaml
import time
from .commands import *

class Client:
    def __init__(self, server_address: str, port: int = 6700):
        self.VERSION = 1
        self.SUPPORTED_VERSIONS = [1]
        self.ENDIANESS = "big"
        self.SERVER_ADDRESS = server_address
        self.PORT = port
        self.WAIT_FOR_RESPONSE = 0.1
        self.MAX_CONTENT_SIZE = 16*1024*1024
        self.MAX_HEADER_LEN = 8*1024
        self.MAX_BYTES_SENT_AT_ONCE = 16*1024
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.SERVER_ADDRESS, self.PORT))
        except ConnectionRefusedError:
            print("Error: This server seems not to be online")
            sys.exit(1)

    # BASIC FUNCTIONS
    def send_packet(self, command: int, metadata: dict, body: bytes = None) -> None:
        # means all header data
        all_data = b""
        # version
        all_data += self.int_to_bytes(self.VERSION, 2)

        # encode header
        header = b""
        header += self.int_to_bytes(command, 4)
        header += yaml.dump(metadata).encode("utf-8")
        header += self.int_to_bytes(0, 32)
        if len(header) > self.MAX_HEADER_LEN:
            raise Exception("header too long")

        # header
        all_data += self.int_to_bytes(len(header), 4)
        all_data += header

        self.socket.send(all_data)

        # body
        body_data = b""
        if body is None:
            body_len = self.int_to_bytes(32, 4)
            body_data += self.int_to_bytes(0, 32)
        else:
            body_len = self.int_to_bytes(len(body)+32, 4)
            body_data += body
            body_data += self.int_to_bytes(0, 32)

        self.socket.send(body_len)

        i = 0
        while True:
            if i+self.MAX_BYTES_SENT_AT_ONCE > len(body_data):
                self.socket.send(body_data[i:])
                break
            self.socket.send(body_data[i:i+self.MAX_BYTES_SENT_AT_ONCE])
            i += self.MAX_BYTES_SENT_AT_ONCE

    def recv_packet(self):
        # version
        version = self.bytes_to_int(self.socket.recv(2))
        if version not in self.SUPPORTED_VERSIONS:
            self.rfap_disconnect()
            raise Exception(f"trying to receive packet of unsupported version (v{version})")

        # header
        header_length = self.bytes_to_int(self.socket.recv(4))
        header_raw = self.socket.recv(header_length)
        command = self.bytes_to_int(header_raw[:4])
        try:
            metadata = yaml.load(header_raw[4:-32], Loader=yaml.SafeLoader)
        except Exception as e:
            print(e)
            print("ERROR DECODING HEADER!")
            return version, command, {}, b""
        header_checksum = header_raw[-32:]
        _ = header_checksum

        # body
        body_length = self.bytes_to_int(self.socket.recv(4))
        body = self.socket.recv(body_length)
        body_checksum = body[-32:]
        _ = body_checksum

        return version, command, metadata, body[:-32]

    # HELPER FUNCTIONS
    def int_to_bytes(self, value: int, bytes_number: int = 4) -> bytes:
        return value.to_bytes(bytes_number, self.ENDIANESS)

    def bytes_to_int(self, value: bytes) -> int:
        return int.from_bytes(value, self.ENDIANESS)

    # IMPLEMENTATION OF RFAP COMMANDS
    def rfap_ping(self) -> None:
        self.send_packet(CMD_PING, {})
        time.sleep(self.WAIT_FOR_RESPONSE)
        self.recv_packet()

    def rfap_disconnect(self) -> None:
        self.send_packet(CMD_DISCONNECT, {})
        time.sleep(self.WAIT_FOR_RESPONSE)
        self.socket.close()

    def rfap_info(self, path: str, verbose: bool = False) -> dict:
        if verbose:
            requireDetails = ["DirectorySize", "ElementsNumber"]
        else:
            requireDetails = []
        self.send_packet(CMD_INFO, {"Path": path, "RequestDetails": requireDetails})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _, = self.recv_packet()
        return metadata

    def rfap_file_read(self, path: str):
        self.send_packet(CMD_FILE_READ, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, body = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            return metadata, b""
        return metadata, body

    def rfap_directory_read(self, path: str, verbose: bool = False):
        if verbose:
            requireDetails = ["DirectorySize", "ElementsNumber"]
        else:
            requireDetails = []
        self.send_packet(CMD_DIRECTORY_READ, {"Path": path, "RequestDetails": requireDetails})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, body = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            return metadata, []
        return metadata, [i for i in body.decode("utf-8").split("\n") if i != ""]

    # TODO optional other commands

