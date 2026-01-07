import subprocess


def run_command(command, output=True, print_output=True):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stderr:
        print(result.stderr)
    if print_output:
        print(result.stdout.strip())
    if output:
        return result.stdout.strip()
    return None
