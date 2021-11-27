
import socket
import yaml
from .commands import *

class Client:
    def __init__(self, server_address, port=3333):
        self.VERSION = 1
        self.SUPPORTED_VERSIONS = [1]
        self.ENDIANESS = "big"
        self.SERVER_ADDRESS = server_address
        self.PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.SERVER_ADDRESS, self.PORT))

    # BASIC FUNCTIONS
    def send_command(self, command: int, metadata: dict, body: bytes = None) -> None:
        # send version
        self.socket.send(self.int_to_bytes(self.VERSION, 2))

        # encode header
        header = b""
        header += self.int_to_bytes(command)
        header += yaml.dump(metadata).encode("utf-8")
        header += self.int_to_bytes(0, 32)

        # send header
        self.socket.send(self.int_to_bytes(len(header)))
        self.socket.send(header)

        # send body
        if body is None:
            self.socket.send(self.int_to_bytes(0))
            return
        self.socket.send(self.int_to_bytes(len(body) + 32))
        self.socket.send(body)
        self.socket.send(self.int_to_bytes(0, 32))

    def recv_command(self):
        # get version
        version = self.bytes_to_int(self.socket.recv(2))
        if version not in self.SUPPORTED_VERSIONS:
            self.socket.close()
            raise Exception("trying to receive packet of unsupported version")

        # get header
        header_length = self.bytes_to_int(self.socket.recv(4))
        header_raw = self.socket.recv(header_length)
        command = self.bytes_to_int(header_raw[:4])
        metadata = yaml.load(header_raw[4:-32])
        header_checksum = header_raw[-32:]

        # get body
        body_length = self.bytes_to_int(self.socket.recv(4))
        body = self.socket.recv(body_length - 32)
        body_checksum = self.socket.recv(32)

        return version, command, metadata, header_checksum, body, body_checksum

    # HELPER FUNCTIONS
    def int_to_bytes(self, value: int, bytes_number: int = 4) -> bytes:
        return value.to_bytes(bytes_number, self.ENDIANESS)

    def bytes_to_int(self, value: bytes) -> int:
        return int.from_bytes(value, self.ENDIANESS)

    # IMPLEMENTATION OF RFAP COMMANDS
    def rfap_ping(self) -> None:
        self.send_command(CMD_PING, {})

    def rfap_disconnect(self) -> None:
        self.send_command(CMD_DISCONNECT, {})
        self.socket.close()

    def rfap_info(self, path: str) -> dict:
        self.send_command(CMD_INFO, {"Path": path})
        _, _, metadata, _, _, _ = self.recv_command()
        return metadata

    # TODO all other commands

