
class UnsupportedRfapVersionError(Exception):
    def __init__(self, version):
        self.version = version
        super().__init__()

    def __str__(self):
        return f"Unsupported rfap version: {self.version}"

class ServerError(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Server sent error"

class HeaderDecodeError(Exception):
    def __init__(self, parent_exception):
        self.parent_exception = parent_exception
        super().__init__()

    def __str__(self):
        return f"Error decoding header: {str(self.parent_exception)}"

class InvalidHeaderLengthError(Exception):
    def __init__(self, header_length):
        self.header_length = header_length
        super().__init__()

    def __str__(self):
        return f"Invalid header length: {self.header_length}"

class ChecksumError(Exception):
    def __init__(self, got, expected):
        self.got = got
        self.expected = expected
        super().__init__()

    def __str__(self):
        return f"checksums don't match: expected {self.expected}, got {self.got}"

