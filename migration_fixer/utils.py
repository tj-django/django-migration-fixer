import shlex
import subprocess
from typing import Tuple

DEFAULT_TIMEOUT = 120


def _decode_message(output: bytes, encoding: str) -> str:
    return output.decode(encoding).strip()


def run_command(command: str, encoding="utf-8", timeout=DEFAULT_TIMEOUT) -> Tuple[bool, str, str]:
    process = subprocess.Popen(
        shlex.split(command),
        encoding=encoding,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        output, error = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        output, error = process.communicate()

    output = output or ''
    error = error or ''

    if isinstance(output, bytes):
        output = _decode_message(output, encoding)

    if isinstance(error, bytes):
        error = _decode_message(error, encoding)

    exit_code = process.poll()
    has_no_errors = exit_code == 0

    return has_no_errors, output, error
