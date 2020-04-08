from shutil import which


def command_exists(command: str) -> bool:
    return which(command) is not None
