import os
import urllib
from shutil import which


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
