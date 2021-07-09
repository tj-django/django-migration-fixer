"""
Create a new django migration with support for fixing conflicts.
"""

import os
import pathlib

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.makemigrations import Command as BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections, router
from django.db.migrations.loader import MigrationLoader
from git import InvalidGitRepositoryError, Repo

from migration_fixer.utils import fix_numbered_migration, no_translations


class Command(BaseCommand):
    """
    Create a new django migration with support for fixing conflicts.
    """

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
        self.default_branch = options["default_branch"]

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

                    current_branch = self.repo.head.ref.name

                    if self.repo.is_dirty():  # pragma: no cover
                        raise CommandError(
                            self.style.ERROR(
                                "Git repository has uncommitted changes. "
                                "Please commit any outstanding changes."
                            )
                        )

                    if self.verbosity >= 2:
                        self.stdout.write(
                            f"Fetching git remote origin changes on: {self.default_branch}"
                        )

                    if current_branch == self.default_branch:  # pragma: no cover
                        for remote in self.repo.remotes:
                            remote.pull(
                                self.default_branch,
                                force=self.force_update,
                            )
                    else:
                        for remote in self.repo.remotes:
                            remote.fetch(
                                f"{self.default_branch}:{self.default_branch}",
                                force=self.force_update,
                            )

                    if self.verbosity >= 2:
                        self.stdout.write(
                            f"Retrieving the last commit sha on: {self.default_branch}"
                        )

                    default_branch_commit = self.repo.commit(self.default_branch)

                    current_commit = self.repo.commit(current_branch)

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

                    # Before anything else, see if there's conflicting apps and drop out
                    # hard if there are any and they don't want to merge
                    conflicts = loader.detect_conflicts()

                    for app_label in conflicts:
                        conflict = conflicts.get(app_label)
                        migration_module, _ = loader.migrations_module(app_label)
                        migration_absolute_path = os.path.join(
                            *migration_module.split(".")
                        )
                        migration_path = pathlib.Path(
                            os.path.join(settings.BASE_DIR, migration_absolute_path)
                        )

                        with migration_path:
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    "Retrieving changed files between "
                                    f"the current branch and {self.default_branch}"
                                )

                            diff_index = default_branch_commit.diff(current_commit)

                            # Files different on the current branch
                            changed_files = [
                                diff.b_path
                                for diff in diff_index
                                if migration_absolute_path
                                in getattr(diff.a_blob, "abspath", "")
                                or migration_absolute_path
                                in getattr(diff.b_blob, "abspath", "")
                            ]

                            # Local migration
                            local_filenames = [
                                os.path.splitext(os.path.basename(p))[0]
                                for p in changed_files
                            ]
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    f"Retrieving the last migration on: {self.default_branch}"
                                )

                            last_remote = [
                                name for name in conflict if name not in local_filenames
                            ]

                            if not last_remote:  # pragma: no cover
                                raise CommandError(
                                    self.style.ERROR(
                                        f"Unable to determine the last migration on: "
                                        f"{self.default_branch}. "
                                        "Please verify the target branch using"
                                        '"-b [target branch]".',
                                    )
                                )

                            last_remote_filename, *rest = last_remote
                            changed_files = changed_files or [
                                f"{fname}.py" for fname in rest
                            ]

                            seed_split = last_remote_filename.split("_")

                            try:
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
                                        start_name=last_remote_filename,
                                        changed_files=changed_files,
                                        writer=(
                                            lambda message: self.stdout.write(message)
                                            if self.verbosity >= 2
                                            else lambda x: x
                                        ),
                                    )
                                else:  # pragma: no cover
                                    raise ValueError(
                                        f"Unable to fix migration: {last_remote_filename}. \n"
                                        f"NOTE: It needs to begin with a number. eg. 0001_*",
                                    )
                            except (ValueError, IndexError, TypeError) as e:
                                self.stderr.write(f"Error: {e}")
                            else:
                                self.stdout.write(self.success_msg)

        else:
            return super(Command, self).handle(*app_labels, **options)
