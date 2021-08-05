import importlib
import os
import pkgutil
import sys
import urllib
from contextlib import contextmanager
from google_drive_downloader import GoogleDriveDownloader
from pathlib import Path
from shutil import which
from typing import Generator, List, T, Union

PathType = Union[os.PathLike, str]
ContextManagerFunctionReturnType = Generator[T, None, None]


def command_exists(command: str) -> bool:
    return which(command) is not None


def download_url_to_file(url: str, file_path: str, force: bool = False) -> None:
    """
    Downloads a url to a local file if it does not already exist. The directory
    path to the download file will be created if it does not exist.

    Parameters
    ----------
    url: ``str``, required.
        The url of the file to download.
    file_path: ``str``, required.
        The path where the file should be saved.
    force: ``bool``, optional (default = ``False``)
        If false, the file is not downloaded if it exists. Otherwise, the
        file will be downloaded no matter what.
    """
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    if os.path.exists(file_path) and not force:
        print(f'Skipping downloading {url}')
        return

    print(f'Downloading {url} to {file_path}')
    urllib.request.urlretrieve(url, file_path)


def download_file_from_google_drive(file_id: str, file_path: str, force: bool = False) -> None:
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    if os.path.exists(file_path) and not force:
        print(f'Skipping downloading file {file_id}')
        return

    print(f'Downloading file {file_id} to {file_path}')
    GoogleDriveDownloader.download_file_from_google_drive(file_id, file_path, overwrite=True)


@contextmanager
def push_python_path(path: PathType) -> ContextManagerFunctionReturnType[None]:
    """
    Prepends the given path to `sys.path`.
    This method is intended to use with `with`, so after its usage, its value willbe removed from
    `sys.path`.
    """
    # In some environments, such as TC, it fails when sys.path contains a relative path, such as ".".
    path = Path(path).resolve()
    path = str(path)
    sys.path.insert(0, path)
    try:
        yield
    finally:
        # Better to remove by value, in case `sys.path` was manipulated in between.
        sys.path.remove(path)


# Borrowed from AllenNLP
def import_module_and_submodules(package_name: str) -> None:
    """
    Import all submodules under the given package.
    Primarily useful so that people using AllenNLP as a library
    can specify their own custom packages and have their custom
    classes get loaded and registered.
    """
    # We don't want to include anything in the test package
    if package_name == 'sacrerouge.tests':
        return

    importlib.invalidate_caches()

    # For some reason, python doesn't always add this by default to your path, but you pretty much
    # always want it when using `--include-package`.  And if it's already there, adding it again at
    # the end won't hurt anything.
    with push_python_path("."):
        # Import at top level
        module = importlib.import_module(package_name)
        path = getattr(module, "__path__", [])
        path_string = "" if not path else path[0]

        # walk_packages only finds immediate children, so need to recurse.
        for module_finder, name, _ in pkgutil.walk_packages(path):
            # Sometimes when you import third-party libraries that are on your path,
            # `pkgutil.walk_packages` returns those too, so we need to skip them.
            if path_string and module_finder.path != path_string:
                continue
            subpackage = f"{package_name}.{name}"
            import_module_and_submodules(subpackage)


def flatten(text: Union[str, List[str]]) -> str:
    if isinstance(text, list):
        return ' '.join(text)
    return text