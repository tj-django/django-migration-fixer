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
    previous_branch_name = ''

    try:
        os.chdir(git_repo.workspace)
        # Clean all untracked files
        git_repo.api.git.clean('-xdf')

        previous_branch_name = git_repo.api.active_branch.name

        target_branch = git_repo.api.heads[target_branch_name]

        target_branch.checkout(force=True)

        yield target_branch

    finally:
        if previous_branch_name:
            git_repo.api.heads[previous_branch_name].checkout(force=True)

        # Clean all untracked files
        git_repo.api.git.clean('-xdf')

        os.chdir(cwd)
