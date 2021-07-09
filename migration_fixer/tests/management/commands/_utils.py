import contextlib
import os
from io import StringIO

from django.core.management import call_command

from migration_fixer.tests.management.commands.conftest import GitRepo


def execute_command(cmd, *args, **kwargs):
    out = StringIO()
    kwargs["stdout"] = out
    kwargs["stderr"] = out
    call_command(cmd, *args, **kwargs)
    output = out.getvalue()

    return output


@contextlib.contextmanager
def temporary_checkout(
    git_repo: GitRepo, default_branch_name: str, target_branch_name: str
):
    cwd = os.getcwd()

    try:
        os.chdir(git_repo.workspace)
        # Clean all untracked files
        git_repo.api.git.clean("-xdf")

        target_branch = git_repo.api.heads[target_branch_name]

        target_branch.checkout(force=True)

        yield target_branch

    finally:
        # Clean all untracked files
        git_repo.api.git.clean("-xdf")

        default_branch = git_repo.api.heads[default_branch_name]

        default_branch.checkout(force=True)

        os.chdir(cwd)
