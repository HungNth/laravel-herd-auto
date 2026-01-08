import subprocess
from typing import Union, List


def run_command(command, capture=True, print_output=True, shell=True):
    result = subprocess.run(
        command,
        shell=shell,
        capture_output=capture,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    
    if print_output and result.stdout:
        print(result.stdout)
    
    return result.stdout.strip()

# def run_command(
#         args: Union[str, List[str]],
#         *,
#         shell: bool = False,
#         capture: bool = True,
#         print_output: bool = True,
# ):
#     if shell:
#         if not isinstance(args, str):
#             raise ValueError("args must be str when shell=True")
#         cmd = args
#     else:
#         if not isinstance(args, (list, tuple)):
#             raise ValueError("args must be list/tuple when shell=False")
#
#         cmd = []
#         for a in args:
#             if a is None:
#                 continue
#             cmd.append(str(a))
#
#     result = subprocess.run(
#         cmd,
#         shell=shell,
#         capture_output=capture,
#         text=True,
#     )
#
#     if result.stderr:
#         print(result.stderr.strip())
#
#     if print_output and result.stdout:
#         print(result.stdout.strip())
#
#     return result.stdout.strip()
