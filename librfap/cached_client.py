
from .client import Client
import time

class CachedClient(Client):
    def __init__(self, server_address: str, port: int = 6700, cache_timeout: tuple = (60, 60, 60)):
        (self.CACHE_INFO_TIMEOUT, self.CACHE_DIRS_TIMEOUT, self.CACHE_FILES_TIMEOUT) = cache_timeout
        self.cache_info = {}
        self.cache_dirs = {}
        self.cache_files = {}
        super().__init__(server_address, port)

    def rfap_info(self, path: str, verbose: bool = True) -> dict:
        if path in self.cache_info and self.cache_info[path]["expires"] > int(time.time()):
            return self.cache_info[path]["data"]
        data = super().rfap_info(path, verbose=True)
        self.cache_info[path] = {
                "data": data,
                "expires": int(time.time())+self.CACHE_INFO_TIMEOUT
                }
        return self.cache_info[path]["data"]

    def rfap_directory_read(self, path: str, verbose: bool = True):
        if path in self.cache_dirs and self.cache_dirs[path]["expires"] > int(time.time()):
            files = self.cache_dirs[path]["files"]
            if path in self.cache_info and self.cache_info[path]["expires"] > int(time.time()):
                data = self.cache_info[path]["data"]
            else:
                data = super().rfap_info(path, verbose=True)
        else:
            data, files = super().rfap_directory_read(path, verbose=True)
        self.cache_dirs[path] = {
                "files": files,
                "expires": int(time.time())+self.CACHE_DIRS_TIMEOUT
                }
        self.cache_info[path] = {
                "data": data,
                "expires": int(time.time())+self.CACHE_INFO_TIMEOUT
                }
        return data, files

    def rfap_file_read(self, path: str):
        if path in self.cache_files and self.cache_files[path]["expires"] > int(time.time()):
            content = self.cache_files[path]["content"]
            if path in self.cache_info and self.cache_info[path]["expires"] > int(time.time()):
                data = self.cache_info[path]["data"]
            else:
                data = super().rfap_info(path)
        else:
            data, content = super().rfap_file_read(path)
        self.cache_files[path] = {
                "data": data,
                "content": content,
                "expires": int(time.time())+self.CACHE_FILES_TIMEOUT
                }
        self.cache_info[path] = {
                "data": data,
                "expires": int(time.time())+self.CACHE_INFO_TIMEOUT
                }
        return data, content

