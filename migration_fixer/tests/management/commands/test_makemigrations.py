"""Tests for `migration_fixer` package."""

import pytest

from migration_fixer.management.commands.makemigrations import Command
from migration_fixer.tests.management.commands.constants import (
    TEST_01_MIGRATION_BRANCH,
    TEST_02_MIGRATION_BRANCH
)
from migration_fixer.tests.management.commands.utils import execute_command, temporary_checkout


@pytest.mark.django_db
def test_run_makemigrations_is_valid_without_any_conflicts(git_repo):
    cmd = Command(git=git_repo.api)

    with temporary_checkout(git_repo, target_branch_name=TEST_01_MIGRATION_BRANCH) as target_branch:
        output1 = execute_command(cmd)
        output2 = execute_command(cmd, fix=True)

    assert target_branch.name == TEST_01_MIGRATION_BRANCH
    assert output1 == "No changes detected\n"
    assert output2 == "No changes detected\n"


@pytest.mark.django_db
def test_run_makemigrations_with_fix_is_valid_for_conflicts(git_repo):
    cmd = Command(git=git_repo.api)

    with temporary_checkout(git_repo, target_branch_name=TEST_02_MIGRATION_BRANCH) as target_branch:
        output = execute_command(cmd, default_branch=TEST_01_MIGRATION_BRANCH, fix=True)

    assert target_branch.name == TEST_02_MIGRATION_BRANCH
    assert output == f'{cmd.success_msg}\n'
