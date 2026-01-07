import subprocess


def add_ssl(path):
    # command = f'herd secure "{path}"'
    command = f'cd /d "{path}" && herd secure'
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True, stderr=subprocess.DEVNULL)
    print('SSL certificate added successfully.')
