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
def temporary_checkout(git_repo):
    cwd = os.getcwd()

    try:
        os.chdir(git_repo.workspace)
        # Clean all untracked files
        git_repo.api.git.clean("-xdf")

        target_branch = git_repo.api.active_branch

        yield target_branch

    finally:
        # Clean all untracked files
        git_repo.api.git.clean("-xdf")

        os.chdir(cwd)
