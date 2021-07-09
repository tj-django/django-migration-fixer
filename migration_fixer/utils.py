import os
import re
from functools import partial
from itertools import count
from pathlib import Path
from typing import Callable, List

DEFAULT_TIMEOUT = 120
MIGRATION_REGEX = "\\((?P<comma>['\"]){app_label}(['\"]),\\s(['\"])(?P<conflict_migration>.*)(['\"])\\),"


def _clean_message(output: str) -> str:
    """Strips the succeeding new line and carriage return characters."""
    return output.rstrip("\n\r")


def _decode_message(output: bytes, encoding: str) -> str:
    """Converts bytes to string, stripping white spaces."""
    return output.decode(encoding).strip()


def _update_migration(conflict_path: Path, app_label: str, prev_migration: str) -> None:
    """Modify the migration file."""
    replace_regex = re.compile(
        MIGRATION_REGEX.format(app_label=app_label),
        re.I | re.M,
    )

    match = replace_regex.search(conflict_path.read_text())

    if match:
        comma = match.group("comma")
        replacement = f"({comma}{app_label}{comma}, {comma}{prev_migration}{comma}),"

        # Update the migration
        output = re.sub(
            replace_regex,
            replacement,
            conflict_path.read_text(),
        )

        # Write to the conflict file.
        conflict_path.write_text(output)
    else:
        raise ValueError(f'Couldn\'t find "{MIGRATION_REGEX}" in {conflict_path.name}')


def migration_sorter(path: str, app_label: str) -> int:
    path = os.path.split(path)[-1]
    parts = path.split("_")
    key = parts[0]

    if not str(key).isdigit():
        raise ValueError(
            f'Unable to fix migration for "{app_label}" app: {path} \n'
            f"NOTE: It needs to begin with a number. eg. 0001_*",
        )

    return int(key)


def fix_numbered_migration(
    *,
    app_label: str,
    migration_path: Path,
    seed: int,
    start_name: str,
    changed_files: List[str],
    writer: Callable[[str], None],
):
    """Resolve migration conflicts for numbered migrations."""
    seen = [start_name]
    counter = count(seed + 1)  # 0537 -> 538
    sorted_changed_files = sorted(
        changed_files, key=partial(migration_sorter, app_label=app_label)
    )

    for path in sorted_changed_files:
        next_ = str(next(counter))

        if len(next_) < 4:
            next_ = f"{next_}".rjust(4, "0")  # 0537

        basename = os.path.basename(path)
        conflict_path = migration_path / basename
        conflict_parts = basename.split("_")

        if str(conflict_parts[0]).isdigit():
            conflict_parts[0] = next_
        else:
            raise ValueError(
                f'Unable to fix migration: "{conflict_path.name}" \n'
                f"NOTE: It needs to begin with a number. eg. 0001_*",
            )

        new_conflict_name = "_".join(conflict_parts)

        conflict_new_path = conflict_path.with_name(new_conflict_name)

        with conflict_path:
            prev_migration = seen[-1]

            writer(
                f'Updating migration "{conflict_path.name}" dependency to {prev_migration}'
            )
            _update_migration(conflict_path, app_label, prev_migration)

            writer(
                f'Renaming migration "{conflict_path.name}" to "{conflict_new_path.name}"'
            )
            # Rename the migration file
            conflict_path.rename(conflict_new_path)

            seen.append(conflict_new_path.stem)


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
