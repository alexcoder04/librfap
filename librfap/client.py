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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.SERVER_ADDRESS, self.PORT))
        except ConnectionRefusedError:
            print("Error: This server seems not to be online")
            sys.exit(1)

    # BASIC FUNCTIONS
    def _send_command(self, command: int, metadata: dict, body: bytes = None) -> None:
        all_data = b""
        # version
        all_data += self.int_to_bytes(self.VERSION, 2)

        # encode header
        header = b""
        header += self.int_to_bytes(command, 4)
        header += yaml.dump(metadata).encode("utf-8")
        header += self.int_to_bytes(0, 32)

        # header
        all_data += self.int_to_bytes(len(header), 4)
        all_data += header

        # body
        if body is None:
            all_data += self.int_to_bytes(32, 4)
        else:
            all_data += self.int_to_bytes(len(body), 4)
            all_data += body

        # send everything
        self.socket.send(all_data)

    def _recv_command(self):
        # receive everything
        data = self.socket.recv(2+4+(16*1024*1024)+4+(16*1024*1024))

        # version
        version = self.bytes_to_int(data[:2])
        if version not in self.SUPPORTED_VERSIONS:
            self.socket.close()
            raise Exception(f"trying to receive packet of unsupported version (v{version})")

        # header
        header_length = self.bytes_to_int(data[2 : 2+4])
        command = self.bytes_to_int(data[2+4 : 2+4+4])
        header_raw = data[2+4+4 : 2+4+(header_length-32)]
        try:
            metadata = yaml.load(header_raw, Loader=yaml.SafeLoader)
        except Exception as e:
            print(e)
            print("ERROR DECODING HEADER!")
            return version, command, {}, None, b"", None
        header_checksum = data[2+4+(header_length-32) : 2+4+header_length]

        # body
        body_length = self.bytes_to_int(data[2+4+header_length : 2+4+header_length+4])
        body = data[2+4+header_length+4 : 2+4+header_length+4+(body_length-32)]
        body_checksum = data[2+4+header_length+4+(body_length-32) : 2+4+header_length+4+body_length]

        return version, command, metadata, header_checksum, body, body_checksum

    def recv_data(self):
        first_version, first_command, first_metadata, _, body, _ = self._recv_command()
        if first_metadata["PacketsTotal"] < 1:
            raise Exception("invalid total packets number")
        if first_metadata["PacketsTotal"] == 1:
            return first_version, first_command, first_metadata, body
        for i in range(first_metadata["PacketsTotal"] - 1):
            this_version, this_command, this_metadata, _, body_part, _ = self._recv_command()
            if this_version != first_version:
                raise Exception("Data in different packets does not match")
            if this_metadata["PacketNumber"] != i+1:
                raise Exception("Data in different packets does not match")
            if this_command != first_command:
                raise Exception("Data in different packets does not match")
            # TODO check if other metadata values match
            body = body + body_part
        return first_version, first_command, first_metadata, body

    def send_data(self, command: int, metadata: dict, body: bytes = None) -> None:
        if body is None:
            metadata["PacketNumber"] = 1
            metadata["PacketsTotal"] = 1
            self._send_command(command, metadata, body)
            return
        if len(body) <= self.MAX_CONTENT_SIZE:
            metadata["PacketNumber"] = 1
            metadata["PacketsTotal"] = 1
            self._send_command(command, metadata, body)
            return
        i = 0
        packets = []
        while True:
            if (i + self.MAX_CONTENT_SIZE) >= len(body):
                packets.append((command, metadata, body[i:]))
                break
            packets.append((command, metadata, body[i : (i+self.MAX_CONTENT_SIZE)]))
            i += self.MAX_CONTENT_SIZE
        metadata["PacketsTotal"] = len(packets)
        for i, p in enumerate(packets):
            metadata["PacketNumber"] = i + 1
            self._send_command(*p)

    # HELPER FUNCTIONS
    def int_to_bytes(self, value: int, bytes_number: int = 4) -> bytes:
        return value.to_bytes(bytes_number, self.ENDIANESS)

    def bytes_to_int(self, value: bytes) -> int:
        return int.from_bytes(value, self.ENDIANESS)

    # IMPLEMENTATION OF RFAP COMMANDS
    def rfap_ping(self) -> None:
        self.send_data(CMD_PING, {})
        time.sleep(self.WAIT_FOR_RESPONSE)
        self.recv_data()

    def rfap_disconnect(self) -> None:
        self.send_data(CMD_DISCONNECT, {})
        time.sleep(self.WAIT_FOR_RESPONSE)
        self.socket.close()

    def rfap_info(self, path: str, verbose: bool = False) -> dict:
        if verbose:
            requireDetails = ["DirectorySize", "ElementsNumber"]
        else:
            requireDetails = []
        self.send_data(CMD_INFO, {"Path": path, "RequestDetails": requireDetails})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, _, = self.recv_data()
        return metadata

    def rfap_file_read(self, path: str):
        self.send_data(CMD_FILE_READ, {"Path": path})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, body = self.recv_data()
        if metadata["ErrorCode"] != 0:
            return metadata, b""
        return metadata, body

    def rfap_directory_read(self, path: str, verbose: bool = False):
        if verbose:
            requireDetails = ["DirectorySize", "ElementsNumber"]
        else:
            requireDetails = []
        self.send_data(CMD_DIRECTORY_READ, {"Path": path, "RequestDetails": requireDetails})
        time.sleep(self.WAIT_FOR_RESPONSE)
        _, _, metadata, body = self.recv_data()
        if metadata["ErrorCode"] != 0:
            return metadata, []
        return metadata, [i for i in body.decode("utf-8").split("\n") if i != ""]

    # TODO optional other commands

