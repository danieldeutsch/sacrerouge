import binascii


def is_gz_file(file_path: str):
    """
    Tests to see if a file is gzipped or not. This was taken from
    https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed

    Returns
    -------
    True if it is gzipped, False otherwise.
    """
    with open(file_path, 'rb') as f:
        return binascii.hexlify(f.read(2)) == b'1f8b'
