import platform
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
        from config import win_herd_sites_path, win_herd_cached_path, win_herd_bin_path
        if not win_herd_sites_path or not win_herd_cached_path or not win_herd_bin_path:
            return exit("Please configure the herd paths in 'config.py' for Windows.")
        herd_sites_path = Path(win_herd_sites_path)
        herd_cached_path = Path(win_herd_cached_path)
        herd_bin_path = Path(win_herd_bin_path)
        
        return herd_sites_path, herd_cached_path, herd_bin_path
    elif is_mac():
        from config import mac_herd_sites_path, mac_herd_cached_path, mac_herd_bin_path
        if not mac_herd_sites_path or not mac_herd_cached_path or not mac_herd_bin_path:
            return exit("Please configure the herd paths in 'config.py' for MacOs.")
        herd_sites_path = Path(mac_herd_sites_path)
        herd_cached_path = Path(mac_herd_cached_path)
        herd_bin_path = Path(mac_herd_bin_path)
        
        return herd_sites_path, herd_cached_path, herd_bin_path
    else:
        return None


def wpcli_path():
    _, _, herd_bin_path = herd_path()
    return herd_bin_path / "wp"

# if __name__ == '__main__':
#     print(herd_path())
#     print(wpcli_path())
