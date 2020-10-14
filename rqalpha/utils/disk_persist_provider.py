# -*- coding: utf-8 -*-


import os

from rqalpha.interface import AbstractPersistProvider


class DiskPersistProvider(AbstractPersistProvider):
    def __init__(self, path="./persist"):
        self._path = path
        try:
            os.makedirs(self._path)
        except:
            pass

    def store(self, key, value):
        assert isinstance(value, bytes), "value must be bytes"
        with open(os.path.join(self._path, key), "wb") as f:
            f.write(value)

    def load(self, key, large_file=False):
        try:
            with open(os.path.join(self._path, key), "rb") as f:
                return f.read()
        except IOError as e:
            return None

    def should_resume(self):
        return False

    def should_run_init(self):
        return False