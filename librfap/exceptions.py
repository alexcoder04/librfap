
class UnsupportedRfapVersionError(Exception):
    def __init__(self, version):
        self.version = version
        self.message = "Unsupported rfap version"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.version}"

class HeaderDecodeError(Exception):
    def __init__(self, parent_exception):
        self.parent_exception = parent_exception
        super().__init__()

    def __str__(self):
        return f"Error decoding header: {str(self.parent_exception)}"

class InvalidHeaderLengthError(Exception):
    def __init__(self, header_length):
        self.header_length = header_length
        self.message = "Header is too long"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.header_length}"

