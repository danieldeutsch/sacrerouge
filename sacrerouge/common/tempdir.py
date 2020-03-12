import shutil
import tempfile
from typing import Optional


class TemporaryDirectory(object):
    """
    Creates a temporary directory that works with a context manager (the python
    ``with`` statement). This class was created because the user is responsible for
    deleting the directory created by ``tempfile.mkdtemp``. Instead, the context
    manager ensures the directory is deleted at the end.

    Example usage::

        with TemporaryDirectory() as temp_dir:
            with open(temp_dir + '/file.txt') as out:
                ...

    Parameters
    ----------
    root: ``str``, optional (default = ``None``)
        The root directory where the temporary directory should be created. If ``None``,
        the ``tempfile.mkdtemp`` default location is used.
    persist: ``bool``, optional (default = False)
        Indicates whether or not the directory should be persist on disk after the
        context closes.
    """
    def __init__(self,
                 root: Optional[str] = None,
                 persist: bool = False) -> None:
        self.root = root
        self.persist = persist

    def __enter__(self):
        self.path = tempfile.mkdtemp(dir=self.root)
        return self.path

    def __exit__(self, *args):
        if not self.persist:
            shutil.rmtree(self.path)
