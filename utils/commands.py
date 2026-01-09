import subprocess


def run_command(command, cwd, capture=True, print_output=True, shell=True, pwsh=False, ):
    if pwsh:
        command = f'pwsh -NoProfile -Command \'{command}\''
    
    if cwd is None:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture,
            text=True,
        )
    else:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            capture_output=capture,
            text=True,
        )
    
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    
    if print_output and result.stdout:
        print(result.stdout)
    
    return result.stdout.strip()


if __name__ == '__main__':
    cmd = 'ls'
    run_command(cmd, pwsh=True)
