import platform
import sys
from pathlib import Path

_OS_NAME = None


def check_os():
    global _OS_NAME
    if _OS_NAME is None:
        _OS_NAME = platform.system().lower()
    return _OS_NAME


def is_linux():
    return check_os() == 'linux'


def is_windows():
    return check_os() == 'windows'


def is_mac():
    return check_os() == 'darwin'


def herd_path():
    if is_windows():
        from config import win_herd_sites_path, win_herd_cached_path
        if not win_herd_sites_path or not win_herd_cached_path:
            return sys.exit("Please configure the herd paths in 'config.py' for Windows.")

        if not Path(win_herd_sites_path).exists():
            return sys.exit(f"The herd sites path does not exist: {win_herd_sites_path}")
        if not Path(win_herd_cached_path).exists():
            return sys.exit(f"The herd cached path does not exist: {win_herd_cached_path}")

        herd_sites_path = Path(win_herd_sites_path).expanduser().resolve()
        herd_cached_path = Path(win_herd_cached_path).expanduser().resolve()

        return herd_sites_path, herd_cached_path
    elif is_mac():
        from config import mac_herd_sites_path, mac_herd_cached_path
        if not mac_herd_sites_path or not mac_herd_cached_path:
            return sys.exit("Please configure the herd paths in 'config.py' for MacOs.")

        if not Path(mac_herd_sites_path).exists():
            return sys.exit(f"The herd sites path does not exist: {mac_herd_sites_path}")
        if not Path(mac_herd_cached_path).exists():
            return sys.exit(f"The herd cached path does not exist: {mac_herd_cached_path}")
        herd_sites_path = Path(mac_herd_sites_path).expanduser().resolve()
        herd_cached_path = Path(mac_herd_cached_path).expanduser().resolve()

        return herd_sites_path, herd_cached_path
    else:
        return None
