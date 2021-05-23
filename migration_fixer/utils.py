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


def run_command(
    command: str, encoding="utf-8", timeout=DEFAULT_TIMEOUT
) -> Tuple[bool, str, str]:
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

    output = output or ""
    error = error or ""

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
    counter = count(seed + 1)  # 0537 -> 538
    sorted_changed_files = sorted(changed_files, key=lambda p: p.split("_")[0])

    for path in sorted_changed_files:
        next_ = next(counter)

        if len(str(next_)) < 4:
            next_ = f"{next_}".rjust(4, "0")  # 0537
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
            "\\((['\"]){app_label}(['\"]),\\s(['\"])(?P<conflict_migration>.*)(['\"])\\),".format(
                app_label=app_label
            ),
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

        # Rename the migration file
        conflict_path.rename(conflict_new_path)

        seen.append(new_conflict_name.strip(".py"))


def fix_migration(
    *,
    app_label: str,
    migration_path: Path,
    start_name: str,
    changed_files: List[str],
):
    seen = [start_name]

    for path in changed_files:
        basename = os.path.basename(path)
        conflict_path = migration_path / basename

        with conflict_path:
            replacement = "('{app_label}', '{prev_migration}'),".format(
                app_label=app_label,
                prev_migration=seen[-1],
            )

            replace_regex = re.compile(
                "\\((['\"]){app_label}(['\"]),\\s(['\"])(?P<conflict_migration>.*)(['\"])\\),".format(
                    app_label=app_label
                ),
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

            seen.append(basename.strip(".py"))
