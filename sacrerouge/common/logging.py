import logging
import os
import sys


def prepare_global_logging(file_path: str = None, silent: bool = False) -> None:
    """
    Sets up the logger. If `file_path` is not `None`, the log is written to that file. If
    `silent` is not `True`, the log will also be written to stdout.
    """
    handlers = []
    if file_path is not None:
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        handlers.append(logging.FileHandler(file_path))
    if not silent:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=handlers
    )
