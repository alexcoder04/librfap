
import socket
import yaml
import time
from .commands import *

class Client:
    def __init__(self, server_address, port=6700):
        self.VERSION = 1
        self.SUPPORTED_VERSIONS = [1]
        self.ENDIANESS = "big"
        self.SERVER_ADDRESS = server_address
        self.PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.SERVER_ADDRESS, self.PORT))

    # BASIC FUNCTIONS
    def send_command(self, command: int, metadata: dict, body: bytes = None) -> None:
        all_data = b""
        # version
        all_data += self.int_to_bytes(self.VERSION, 2)

        # encode header
        header = b""
        header += self.int_to_bytes(command)
        header += yaml.dump(metadata).encode("utf-8")
        header += self.int_to_bytes(0, 32)

        # header
        all_data += self.int_to_bytes(len(header), 3)
        all_data += header

        # body
        if body is None:
            all_data += self.int_to_bytes(32, 3)
        else:
            all_data += self.int_to_bytes(len(body), 3)
            all_data += body

        # send everything
        self.socket.send(all_data)

    def recv_command(self):
        # receive everything
        data = self.socket.recv(2+3+(16*1024*1024)+3+(16*1024*1024))

        # version
        version = self.bytes_to_int(data[:2])
        if version not in self.SUPPORTED_VERSIONS:
            self.socket.close()
            raise Exception(f"trying to receive packet of unsupported version (v{version})")

        # header
        header_length = self.bytes_to_int(data[2 : 2+3])
        command = self.bytes_to_int(data[2+3 : 2+3+4])
        header_raw = data[2+3+4 : 2+3+4+(header_length-4-32)]
        try:
            metadata = yaml.load(header_raw, Loader=yaml.SafeLoader)
        except Exception as e:
            print(e)
            print("ERROR DECODING HEADER!")
            self.socket.close()
            exit(1)
        header_checksum = data[2+3+(header_length-32) : 2+3+header_length]

        # body
        body_length = self.bytes_to_int(data[2+3+header_length : 2+3+header_length+3])
        body = data[2+3+header_length+3 : 2+3+header_length+3+(body_length-32)]
        body_checksum = data[2+3+header_length+3+(body_length-32) : 2+3+header_length+3+body_length]

        return version, command, metadata, header_checksum, body, body_checksum

    # HELPER FUNCTIONS
    def int_to_bytes(self, value: int, bytes_number: int = 4) -> bytes:
        return value.to_bytes(bytes_number, self.ENDIANESS)

    def bytes_to_int(self, value: bytes) -> int:
        return int.from_bytes(value, self.ENDIANESS)

    # IMPLEMENTATION OF RFAP COMMANDS
    def rfap_ping(self) -> None:
        self.send_command(CMD_PING, {})
        self.recv_command()

    def rfap_disconnect(self) -> None:
        self.send_command(CMD_DISCONNECT, {})
        self.socket.close()

    def rfap_info(self, path: str) -> dict:
        self.send_command(CMD_INFO, {"Path": path})
        _, _, metadata, _, _, _ = self.recv_command()
        return metadata

    # TODO all other commands

