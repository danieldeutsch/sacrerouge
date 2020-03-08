import bz2
import gzip
import json
import os
from typing import Any


class JsonlWriter(object):
    """
    The ``JsonlWriter`` is a layer of abstraction around writing data to jsonl
    files. The writer will automatically serialize the input objects into json
    strings, then write them to an output file, one object per line. The data
    will be written as plain text or as bytes, depending on the extension of
    the output file. Current supported binary formats are gzip (``.gz``) and
    bz2 (``.bz2``). All other extensions will use plain text.

    The class should be used the same way that a built-in file handler works::

        with JsonlWriter('/path/to/file.jsonl.gz') as out:
            data = ...  # some data to serialize
            out.write(data)

    Parameters
    ----------
    file_path: ``str``
        The path to the file where the data should be written.
    """
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def __enter__(self):
        dirname = os.path.dirname(self.file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        if self.file_path.endswith('.gz'):
            self.file_handler = gzip.open(self.file_path, 'wb')
            self.binary = True
        elif self.file_path.endswith('.bz2'):
            self.file_handler = bz2.open(self.file_path, 'wb')
            self.binary = True
        else:
            self.file_handler = open(self.file_path, 'w')
            self.binary = False
        return self

    def write(self, object: Any) -> None:
        """
        Serializes the input object to a json string and writes it to the file.

        Parameters
        ----------
        object: ``Any``
            The object to write to the file.
        """
        string = json.dumps(object)
        if self.binary:
            self.file_handler.write(string.encode() + b'\n')
        else:
            self.file_handler.write(string + '\n')

    def __exit__(self, *args):
        self.file_handler.close()
