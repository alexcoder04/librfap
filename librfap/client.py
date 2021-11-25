
import os

class Client:
    def __init__(self, server_address, port=1634, public_key=None, private_key=None):
        if public_key is None:
            public_key = self.get_key_file(0)
        if private_key is None:
            private_key = self.get_key_file(1)
        # TODO

    def send_command(self):
        pass

    def get_key_file(self, key):
        if os.name != "posix":
            raise Exception(f"{os.name} system is not supported")
            # TODO other os support
        XDG_DATA_HOME = os.getenv("XDG_DATA_HOME")
        if XDG_DATA_HOME is None:
            XDG_DATA_HOME = os.path.join(os.getenv("HOME"), ".local", "share")
        DATA_DIR = os.path.join(XDG_DATA_HOME, "rfap")
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR)

        if key == 1:
            filename = "key.priv"
        elif key == 0:
            filename = "key.pub"
        else:
            raise Exception("invalid key")

        if os.path.isfile(os.path.join(DATA_DIR, filename)):
            return os.path.join(DATA_DIR, filename)
        raise Exception("key file does not exist")

