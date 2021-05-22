import os
import re
import shlex
import subprocess
from itertools import count
from pathlib import Path
from typing import Tuple, List

DEFAULT_TIMEOUT = 120


def _clean_message(output: str) -> str:
    return output.rstrip("\n\r")


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

    output = _clean_message(output)
    error = _clean_message(error)

    exit_code = process.poll()
    has_no_errors = exit_code == 0

    return has_no_errors, output, error


def fix_numbered_migration(
    *,
    app_label: str,
    migration_path: Path,
    seed: int,
    start_name: str,
    changed_files: List[str],
):
    seen = [start_name]
    prev_ = min(seed - 1, 1)
    counter = count(seed + 1)  # 0537 -> 538
    sorted_changed_files = sorted(changed_files, key=lambda p: p.split("_")[0])

    if len(str(prev_)) < 4:
        prev_ = f"{prev_}".rjust(4, '0')  # 0537
    else:
        prev_ = str(prev_)

    prev_path = list(migration_path.glob(f"*{prev_}*"))

    if prev_path:
        prev_path = prev_path[0]

    before = [prev_path.stem]

    for i, path in enumerate(sorted_changed_files):
        next_ = next(counter)

        if len(str(next_)) < 4:
            next_ = f"{next_}".rjust(4, '0')  # 0537
        else:
            next_ = str(next_)

        basename = os.path.basename(path)
        conflict_path = migration_path / basename
        conflict_parts = basename.split("_")

        conflict_parts[0] = next_

        new_conflict_name = "_".join(conflict_parts)

        conflict_new_path = conflict_path.with_name(new_conflict_name)

        replacement = "('{app_label}', '{prev_migration}'),".format(
            app_label=app_label,
            prev_migration=seen[-1],
        )

        replace_regex = re.compile(
            "\\('{app_label}',\\s(['\"]){conflict}(['\"])\\),".format(app_label=app_label, conflict=before[-1]),
            re.I | re.M,
        )

        # Update the migration
        output = re.sub(
            replace_regex,
            replacement,
            conflict_path.read_text(),
        )

        # Write to the conflict file.
        conflict_path.write_text(output)

        before.append(basename.strip(".py"))

        # Rename the migration file
        conflict_path.rename(conflict_new_path)

        seen.append(new_conflict_name.strip('.py'))


def fix_migration(*, app_label, migration_path, start_name, changed_files):
    pass
