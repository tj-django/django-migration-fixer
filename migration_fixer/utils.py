import os
import re
from importlib import import_module
from itertools import count
from pathlib import Path
from typing import Callable, List, Optional

from django.db.migrations.graph import MigrationGraph

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
    regex = MIGRATION_REGEX.format(app_label=app_label)
    replace_regex = re.compile(regex, re.I)

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
    else:  # pragma: no cover
        raise ValueError(f'Couldn\'t find "{regex}" in {conflict_path.name}')


def migration_sorter(path: str, app_label: str) -> int:
    path = os.path.split(path)[-1]
    parts = path.split("_")
    key = parts[0]

    if not str(key).isdigit():
        raise ValueError(
            f'Unable to fix migration for "{app_label}" app: {path}\n'
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
) -> None:
    """Resolve migration conflicts for numbered migrations."""
    seen = [start_name]
    counter = count(seed + 1)  # 0537 -> 538

    for path in changed_files:
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


def get_filename(path: str) -> str:
    """Return the file name from a path."""
    return os.path.splitext(os.path.basename(path))[0]


def get_migration_module_path(migration_module_path: str) -> Path:
    try:
        migration_module = import_module(migration_module_path)
    except ImportError as e:
        if "bad magic number" in str(e):
            raise ImportError(
                f"Couldn't import {migration_module_path} as it appears to be a stale .pyc file."
            ) from e
        else:
            raise

    return Path(os.path.dirname(os.path.abspath(migration_module.__file__)))


def sibling_nodes(graph: MigrationGraph, app_name: Optional[str] = None) -> List[str]:
    """
    Return all sibling nodes that have the same parent
    - it's usually the result of a VCS merge and needs some user input.
    """
    siblings = set()

    for node in graph.nodes:
        if len(graph.node_map[node].children) > 1 and (
            not app_name or app_name == node[0]
        ):
            for child in graph.node_map[node].children:
                siblings.add(child[-1])

    return sorted(siblings)
