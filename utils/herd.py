import subprocess


def add_ssl(path):
    print('Adding SSL for Herd...')
    command = 'herd secure'
    subprocess.run(command, cwd=path, shell=True, stdout=subprocess.PIPE, text=True, stderr=subprocess.DEVNULL)
    print('SSL certificate added successfully.')


def is_herd_running():
    try:
        result = subprocess.run('herd help', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        text = 'The Herd Desktop application is not running. Please start Herd and try again.'
        if text in result.stdout:
            return False
        return True
    except FileNotFoundError:
        print('Herd command not found. Please ensure Herd is installed and accessible in your PATH.')
        return False
