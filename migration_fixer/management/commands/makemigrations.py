import os
import os
import pathlib
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.management.base import (
    CommandError,
    no_translations,
)
from django.core.management.commands.makemigrations import Command as BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections, router
from django.db.migrations.loader import MigrationLoader

from migration_fixer.utils import run_command, fix_migration, fix_numbered_migration


class Command(BaseCommand):
    help = "Creates new migration(s) for apps."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Fix django migrations using a diff of the default branch.",
        )
        parser.add_argument(
            "-b",
            "--default-branch",
            help="The name of the default branch.",
            default="main",
        )
        super().add_arguments(parser)

    @no_translations
    def handle(self, *app_labels, **options):
        self.merge = options["merge"]
        self.fix = options["fix"]
        self.default_branch = options["default_branch"]

        if self.fix:
            try:
                super().handle(*app_labels, **options)
            except CommandError as e:
                [message] = e.args
                if "Conflicting migrations" in message:
                    git_setup, git_setup_output, git_setup_error = run_command(
                        "git status"
                    )

                    if not git_setup:
                        raise CommandError(
                            self.style.ERROR(
                                f"VCS is not yet setup. "
                                f'Please run (git init) \n"{git_setup_output or git_setup_error}"'
                            )
                        )

                    (
                        get_current_branch,
                        get_current_branch_output,
                        get_current_branch_error,
                    ) = run_command("git branch --show-current")

                    if not get_current_branch:
                        raise CommandError(
                            self.style.ERROR(
                                f"Unable to determine the current branch: "
                                f'"{get_current_branch_output or get_current_branch_error}"'
                            )
                        )

                    pull_command = (
                        "git pull"
                        if get_current_branch_output == self.default_branch
                        else f"git fetch --depth=1 origin {self.default_branch}:{self.default_branch}"
                    )

                    # Pull the last commit
                    git_pull, git_pull_output, git_pull_error = run_command(
                        pull_command
                    )

                    if not git_pull:
                        raise CommandError(
                            self.style.ERROR(
                                f"Error pulling branch ({self.default_branch}) changes: "
                                f'"{git_pull_output or git_pull_error}"'
                            )
                        )

                    head_sha, head_sha_output, head_sha_error = run_command(
                        f"git rev-parse {self.default_branch}"
                    )

                    if not head_sha:
                        raise CommandError(
                            self.style.ERROR(
                                f"Error determining head sha on ({self.default_branch}): "
                                f'"{head_sha_output or head_sha_error}"'
                            )
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

                    # Before anything else, see if there's conflicting apps and drop out
                    # hard if there are any and they don't want to merge
                    conflicts = loader.detect_conflicts()

                    app_labels = app_labels or [
                        app_label
                        for app_label in settings.INSTALLED_APPS
                        if app_label in conflicts
                    ]

                    for app_label in app_labels:
                        conflict = conflicts.get(app_label)
                        migration_module, _ = loader.migrations_module(app_label)
                        migration_absolute_path = os.path.join(
                            *migration_module.split(".")
                        )
                        migration_path = pathlib.Path(
                            os.path.join(settings.BASE_DIR, migration_absolute_path)
                        )

                        with migration_path:
                            (
                                get_changed_files,
                                get_changed_files_output,
                                get_changed_files_error,
                            ) = run_command(
                                f"git diff --diff-filter=ACMUXTR --name-only {self.default_branch}"
                            )

                            if not get_changed_files:
                                raise CommandError(
                                    self.style.ERROR(
                                        f"Error retrieving changed files on ({self.default_branch}): "
                                        f'"{get_changed_files_output or get_changed_files_error}"'
                                    )
                                )
                            # Files different on the current branch
                            changed_files = [
                                fname
                                for fname in get_changed_files_output.split("\n")
                                if migration_absolute_path in fname
                            ]
                            # Local migration
                            local_filenames = [
                                os.path.splitext(os.path.basename(p))[0]
                                for p in changed_files
                            ]
                            last_remote = [
                                fname
                                for fname in conflict
                                if fname not in local_filenames
                            ]

                            if not last_remote:
                                raise CommandError(
                                    self.style.ERROR(
                                        f"Unable to determine the last migration on: "
                                        f"{self.default_branch}",
                                    )
                                )

                            last_remote_filename, *rest = last_remote
                            changed_files = changed_files or [
                                f"{fname}.py" for fname in rest
                            ]

                            seed_split = last_remote_filename.split("_")

                            if (
                                seed_split
                                and len(seed_split) > 1
                                and str(seed_split[0]).isdigit()
                            ):
                                fix_numbered_migration(
                                    app_label=app_label,
                                    migration_path=migration_path,
                                    seed=int(seed_split[0]),
                                    start_name=last_remote_filename,
                                    changed_files=changed_files,
                                )
                            else:
                                fix_migration(
                                    app_label=app_label,
                                    migration_path=migration_path,
                                    start_name=last_remote_filename,
                                    changed_files=changed_files,
                                )

        else:
            return super(Command, self).handle(*app_labels, **options)
