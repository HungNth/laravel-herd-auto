import platform
from pathlib import Path
from utils.commands import run_command

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
    wpcli = Path(herd_bin_path / "wp")
    
    result = run_command(f"{wpcli} --version")
    
    if "WP-CLI" not in result:
        print("WP-CLI is not installed or not found in the expected path.")
        print("Installing WP-CLI...")
        install_wp_cli()
        return wpcli
    else:
        print("WP-CLI is installed on your computer.")
        return wpcli


def install_wp_cli():
    _, _, herd_bin_path = herd_path()
    
    if is_windows():
        command = (
            f'cd /d "{herd_bin_path}" && '
            f'curl -L -O "https://raw.github.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" && '
            f'echo @ECHO OFF > wp.bat && echo php "%~dp0wp-cli.phar" %* >> wp.bat'
        )
        run_command(command)
        print("WP-CLI is installed on your computer.")
    elif is_mac():
        command = (
            f'curl -O "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" && '
            f'chmod +x wp-cli.phar && '
            fr'mv wp-cli.phar ~/Library/Application\ Support/Herd/bin/wp'
        )
        run_command(command)


if __name__ == '__main__':
    wpcli_path()
