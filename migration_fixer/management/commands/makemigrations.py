"""
Create a new django migration with support for fixing conflicts.
"""

import os
from functools import partial

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.makemigrations import Command as BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections, router
from django.db.migrations.loader import MigrationLoader
from git import GitCommandError, InvalidGitRepositoryError, Repo

from migration_fixer.utils import (
    fix_numbered_migration,
    get_filename,
    get_migration_module_path,
    migration_sorter,
    no_translations,
)


class Command(BaseCommand):
    """
    Create a new django migration with support for fixing conflicts.
    """

    help = "Creates new migration(s) for apps and fix conflicts."
    success_msg = "Successfully fixed migrations."

    def __init__(self, *args, repo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd = os.getcwd()
        self.repo = repo or Repo.init(self.cwd)

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Fix migrations conflicts.",
        )
        parser.add_argument(
            "-b",
            "--default-branch",
            help="The name of the default branch.",
            default="main",
        )
        parser.add_argument(
            "-s",
            "--skip-default-branch-update",
            help="Skip pulling the latest changes from the default branch.",
            action="store_true",
        )
        parser.add_argument(
            "-r",
            "--remote",
            help="Git remote.",
            default="origin",
        )
        parser.add_argument(
            "-f",
            "--force-update",
            help="Force update the default branch.",
            action="store_true",
        )
        super().add_arguments(parser)

    @no_translations
    def handle(self, *app_labels, **options):
        self.merge = options["merge"]
        self.fix = options["fix"]
        self.force_update = options["force_update"]
        self.skip_default_branch_update = options["skip_default_branch_update"]
        self.default_branch = options["default_branch"]
        self.remote = options["remote"]

        if self.fix:
            try:
                super().handle(*app_labels, **options)
            except CommandError as e:
                [message] = e.args
                if "Conflicting migrations" in message:
                    if self.verbosity >= 2:
                        self.stdout.write("Verifying git repository...")

                    try:
                        self.repo.git_dir and self.repo.head.commit
                    except (ValueError, InvalidGitRepositoryError):
                        is_git_repo = False
                    else:
                        is_git_repo = True

                    if not is_git_repo:
                        raise CommandError(
                            self.style.ERROR(
                                f"Git repository is not yet setup. "
                                "Please run (git init) in"
                                f'\n"{self.cwd}"'
                            )
                        )

                    if self.verbosity >= 2:
                        self.stdout.write("Retrieving the current branch...")

                    if self.repo.is_dirty():  # pragma: no cover
                        raise CommandError(
                            self.style.ERROR(
                                "Git repository has uncommitted changes. "
                                "Please commit any outstanding changes."
                            )
                        )

                    if not self.skip_default_branch_update:
                        if self.verbosity >= 2:
                            self.stdout.write(
                                f"Fetching git remote {self.remote} changes on: {self.default_branch}"
                            )

                        try:
                            remote = self.repo.remotes[self.remote]
                            remote.fetch(
                                f"{self.default_branch}:{self.default_branch}",
                                force=self.force_update,
                            )
                        except GitCommandError:  # pragma: no cover
                            try:
                                remote = self.repo.remotes[self.remote]
                                remote.pull(
                                    self.default_branch,
                                    force=self.force_update,
                                )
                            except GitCommandError as e:
                                raise CommandError(
                                    self.style.ERROR(
                                        f"Unable to retrieve changes from {self.remote} branch "
                                        f"'{self.default_branch}': {e.stderr}",
                                    ),
                                )

                    default_branch_commit = self.repo.commit(self.default_branch)
                    current_commit = self.repo.head.commit

                    if self.verbosity >= 2:
                        self.stdout.write(
                            f"Retrieving the last commit sha on: {self.default_branch}"
                        )

                    # Load the current graph state. Pass in None for the connection so
                    # the loader doesn't try to resolve replaced migrations from DB.
                    loader = MigrationLoader(None, ignore_no_migrations=True)

                    # Raise an error if any migrations are applied before their dependencies.
                    consistency_check_labels = {
                        config.label for config in apps.get_app_configs()
                    }
                    # Non-default databases are only checked if database routers used.
                    aliases_to_check = (
                        connections if settings.DATABASE_ROUTERS else [DEFAULT_DB_ALIAS]
                    )
                    for alias in sorted(aliases_to_check):
                        connection = connections[alias]
                        if connection.settings_dict[
                            "ENGINE"
                        ] != "django.db.backends.dummy" and any(
                            # At least one model must be migrated to the database.
                            router.allow_migrate(
                                connection.alias,
                                app_label,
                                model_name=model._meta.object_name,
                            )
                            for app_label in consistency_check_labels
                            for model in apps.get_app_config(app_label).get_models()
                        ):
                            loader.check_consistent_history(connection)

                    conflict_leaf_nodes = loader.detect_conflicts()

                    for app_label, leaf_nodes in conflict_leaf_nodes.items():
                        migration_module, _ = loader.migrations_module(app_label)
                        migration_path = get_migration_module_path(migration_module)

                        with migration_path:
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    "Retrieving changed files between "
                                    f"the current branch and {self.default_branch}"
                                )

                            try:
                                diff_index = default_branch_commit.diff(current_commit)

                                # Files different on the current branch
                                changed_files = [
                                    diff.b_path
                                    for diff in diff_index
                                    if (
                                        str(migration_path)
                                        in getattr(diff.a_blob, "abspath", "")
                                        or str(migration_path)
                                        in getattr(diff.b_blob, "abspath", "")
                                    )
                                ]

                                sorted_changed_files = sorted(
                                    changed_files,
                                    key=partial(migration_sorter, app_label=app_label),
                                )

                                # Local migration
                                local_filenames = [
                                    get_filename(p) for p in sorted_changed_files
                                ]

                                # Calculate the last changed file on the default branch
                                conflict_bases = [
                                    name
                                    for name in leaf_nodes
                                    if name not in local_filenames
                                ]

                                if not conflict_bases:  # pragma: no cover
                                    raise CommandError(
                                        self.style.ERROR(
                                            f"Unable to determine the last migration on: "
                                            f"{self.default_branch}. "
                                            "Please verify the target branch using"
                                            '"-b [target branch]".',
                                        )
                                    )

                                conflict_base = conflict_bases[0]

                                if self.verbosity >= 2:
                                    self.stdout.write(
                                        f"Retrieving the last migration on: {self.default_branch}"
                                    )

                                seed_split = conflict_base.split("_")

                                if (
                                    seed_split
                                    and len(seed_split) > 1
                                    and str(seed_split[0]).isdigit()
                                ):
                                    if self.verbosity >= 2:
                                        self.stdout.write(
                                            "Fixing numbered migration..."
                                        )

                                    fix_numbered_migration(
                                        app_label=app_label,
                                        migration_path=migration_path,
                                        seed=int(seed_split[0]),
                                        start_name=conflict_base,
                                        changed_files=sorted_changed_files,
                                        writer=(
                                            lambda m: self.stdout.write(m)
                                            if self.verbosity >= 2
                                            else lambda x: x
                                        ),
                                    )
                                else:  # pragma: no cover
                                    raise ValueError(
                                        f"Unable to fix migration: {conflict_base}. \n"
                                        f"NOTE: It needs to begin with a number. eg. 0001_*",
                                    )
                            except (ValueError, IndexError, TypeError) as e:
                                self.stderr.write(f"Error: {e}")
                            else:
                                self.stdout.write(self.success_msg)

        else:
            return super(Command, self).handle(*app_labels, **options)
