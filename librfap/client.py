#!/usr/bin/env python3

from .commands import *
from .exceptions import *
import hashlib
import socket
import time
import yaml

class Client:
    def __init__(self, server_address: str, port: int = 6700):
        self.VERSION = 2
        self.SUPPORTED_VERSIONS = [2]
        self.ENDIANESS = "big"
        self.WAIT_FOR_RESPONSE = 0.1
        self.MAX_HEADER_LEN = 8*1024
        self.MAX_BYTES_SENT_AT_ONCE = 16*1024

        self.SERVER_ADDRESS = server_address
        self.PORT = port
        self.alive = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.SERVER_ADDRESS, self.PORT))
        except ConnectionRefusedError:
            self.fatal_crash("server seems not to be online")
            raise

    # BASIC FUNCTIONS
    def send_packet(self, command: int, metadata: dict, body: bytes = None) -> None:
        command_bytes = self.int_to_bytes(command, 4)
        metadata_bytes = yaml.dump(metadata).encode("utf-8")
        checksum = hashlib.sha256(command_bytes + metadata_bytes).digest()

        if len(command_bytes+metadata_bytes+checksum) > self.MAX_HEADER_LEN:
            raise InvalidHeaderLengthError(len(command_bytes+metadata_bytes+checksum))

        header_data = self.int_to_bytes(self.VERSION, 2)\
                + self.int_to_bytes(len(command_bytes+metadata_bytes))\
                + command_bytes + metadata_bytes + checksum

        self.socket.send(header_data)

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
            self.fatal_crash("invalid rfap version")
            raise UnsupportedRfapVersionError(version)

        # header
        header_length = self.bytes_to_int(self.socket.recv(4))
        header_raw = self.socket.recv(header_length)
        command = self.bytes_to_int(header_raw[:4])
        try:
            metadata = yaml.load(header_raw[4:-32], Loader=yaml.SafeLoader)
        except Exception as e:
            raise HeaderDecodeError(e)
        header_checksum = header_raw[-32:]
        _ = header_checksum

        # body
        body_length = self.bytes_to_int(self.socket.recv(4))
        body = b""
        while len(body) < body_length:
            body += self.socket.recv(self.MAX_BYTES_SENT_AT_ONCE)
        body_checksum = body[-32:]
        _ = body_checksum

        return version, command, metadata, body[:-32]

    # HELPER FUNCTIONS
    def int_to_bytes(self, value: int, bytes_number: int = 4) -> bytes:
        return value.to_bytes(bytes_number, self.ENDIANESS)

    def bytes_to_int(self, value: bytes) -> int:
        return int.from_bytes(value, self.ENDIANESS)

    def fatal_crash(self, message: str = ""):
        print(f"ERROR: librfap crashed: {message}")
        self.socket.close()
        self.alive = False

    # IMPLEMENTATION OF RFAP COMMANDS
    # server commands
    def rfap_ping(self) -> None:
        self.send_packet(CMD_PING, {})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise # TODO

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

    # file commands
    def rfap_file_read(self, path: str):
        self.send_packet(CMD_FILE_READ, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, body = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            return metadata, b""
        return metadata, body

    def rfap_file_delete(self, path: str):
        self.send_packet(CMD_FILE_DELETE, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot delete file {path}")

    def rfap_file_create(self, path: str):
        self.send_packet(CMD_FILE_CREATE, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot create file {path}")

    def rfap_file_copy(self, source: str, destin: str):
        self.send_packet(CMD_FILE_COPY, {"Path": source, "Destination": destin})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot copy {source} to {destin}")

    def rfap_file_move(self, source: str, destin: str):
        self.send_packet(CMD_FILE_MOVE, {"Path": source, "Destination": destin})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot move {source} to {destin}")

    def rfap_file_write(self, path: str, data: bytes):
        self.send_packet(CMD_FILE_WRITE, {"Path": path}, data)
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"cannot write file {path}")

    # directory commands
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

    def rfap_directory_delete(self, path: str):
        self.send_packet(CMD_DIRECTORY_DELETE, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot delete dir {path}")

    def rfap_directory_create(self, path: str):
        self.send_packet(CMD_DIRECTORY_CREATE, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot create dir {path}")

    def rfap_directory_copy(self, source: str, destin: str):
        self.send_packet(CMD_DIRECTORY_COPY, {"Path": source, "Destination": destin})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot copy {source} to {destin}")

    def rfap_directory_move(self, source: str, destin: str):
        self.send_packet(CMD_DIRECTORY_MOVE, {"Path": source, "Destination": destin})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _ = self.recv_packet()
        if metadata["ErrorCode"] != 0:
            raise Exception(f"Cannot move {source} to {destin}")

