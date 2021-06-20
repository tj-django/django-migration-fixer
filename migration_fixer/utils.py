import os
import re
import shlex
import subprocess
from itertools import count
from pathlib import Path
from typing import List, Tuple

DEFAULT_TIMEOUT = 120
MIGRATION_REGEX = (
    "\\((['\"]){app_label}(['\"]),\\s(['\"])(?P<conflict_migration>.*)(['\"])\\),"
)


def _clean_message(output: str) -> str:
    return output.rstrip("\n\r")


def _decode_message(output: bytes, encoding: str) -> str:
    return output.decode(encoding).strip()


def run_command(
    command: str, encoding: str = "utf-8", timeout: int = DEFAULT_TIMEOUT
) -> Tuple[bool, str, str]:
    command = shlex.split(command)
    process = subprocess.Popen(
        command,
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


def _update_migration(conflict_path: Path, app_label: str, seen: List[str]) -> None:
    replacement = "('{app_label}', '{prev_migration}'),".format(
        app_label=app_label,
        prev_migration=seen[-1],
    )

    replace_regex = re.compile(
        MIGRATION_REGEX.format(app_label=app_label),
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
        next_ = str(next(counter))

        if len(next_) < 4:
            next_ = f"{next_}".rjust(4, "0")  # 0537

        basename = os.path.basename(path)
        conflict_path = migration_path / basename
        conflict_parts = basename.split("_")

        conflict_parts[0] = next_

        new_conflict_name = "_".join(conflict_parts)

        conflict_new_path = conflict_path.with_name(new_conflict_name)

        with conflict_path:
            _update_migration(conflict_path, app_label, seen)

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
            _update_migration(conflict_path, app_label, seen)

            seen.append(basename.strip(".py"))


def no_translations(handle_func):
    """Decorator that forces a command to run with translations deactivated."""

    def wrapped(*args, **kwargs):
        from django.utils import translation

        saved_locale = translation.get_language()
        translation.deactivate_all()
        try:
            res = handle_func(*args, **kwargs)
        finally:
            if saved_locale is not None:
                translation.activate(saved_locale)
        return res

    return wrapped
