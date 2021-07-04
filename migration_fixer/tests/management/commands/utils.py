import contextlib
import os
from io import StringIO

from django.core.management import call_command


def execute_command(cmd, *args, **kwargs):
    out = StringIO()
    kwargs["stdout"] = out
    call_command(cmd, *args, **kwargs)
    output = out.getvalue()

    return output


@contextlib.contextmanager
def temporary_checkout(git_repo, target_branch_name):
    cwd = os.getcwd()

    try:
        os.chdir(git_repo.workspace)
        # Clean all untracked files
        git_repo.api.git.clean("-xdf")

        for remote in git_repo.api.remotes:
            remote.fetch(target_branch_name, force=True)

        target_branch = git_repo.api.heads[target_branch_name]

        target_branch.checkout(force=True)

        yield target_branch

    finally:
        # Clean all untracked files
        git_repo.api.git.clean("-xdf")

        os.chdir(cwd)
