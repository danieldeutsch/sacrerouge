import bz2
import gzip
import json
import jsons
from allennlp.common.file_utils import cached_path
from typing import Any, List, Optional, Type

from sacrerouge.io.util import is_gz_file


class JsonlReader(object):
    """
    The `JsonlReader` is a layer of abstraction around reading serialized
    objects from a jsonl file. The reader will automatically deserialize and return
    one object from each line in the file. The data in the file will be decoded
    from a binary file depending on the extension of the file name. Current
    supported binary formats are gzip (``.gz``) and bz2 (``.bz2``). For gzip only,
    this will also inspect the file to see if it's gzipped in addition to checking
    the extension.

    The class should be used the same way that a built-in file handler works::

        with JsonlReader('/path/to/file.jsonl.gz') as f:
            for data in f:
                ...

    The class uses the cached path functionality from AllenNLP, so it is also
    possible to pass a url to the constructor.

    Parameters
    ----------
    file_path: ``str``
        The path to the file where the data should be read.
    cls: ``Optional[Type]``
        The type that the object should be loaded as.
    """
    def __init__(self, file_path: str, cls: Optional[Type] = None) -> None:
        self.file_path = cached_path(file_path)
        self.cls = cls

    def __enter__(self):
        self.binary = False
        if self.file_path.endswith('.gz') or is_gz_file(self.file_path):
            self.file_handler = gzip.open(self.file_path, 'rb')
            self.binary = True
        elif self.file_path.endswith('.bz2'):
            self.file_handler = bz2.open(self.file_path, 'rb')
            self.binary = True
        else:
            self.file_handler = open(self.file_path, 'r')
            self.binary = False
        return self

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        for line in self.file_handler:
            if self.binary:
                line = line.decode()
            return jsons.loads(line, self.cls)
        raise StopIteration

    def __exit__(self, *args):
        self.file_handler.close()

    def read(self) -> List[Any]:
        """Reads all of the instances into a list."""
        with self:
            return [instance for instance in self]
