"""Tests for `migration_fixer` package."""

import pytest
from django.core.management.base import CommandError

from migration_fixer.management.commands.makemigrations import Command
from migration_fixer.tests.management.commands._constants import (
    TEST_01_MIGRATION_BRANCH,
    TEST_02_MIGRATION_BRANCH,
    TEST_03_MIGRATION_BRANCH,
    TEST_04_MIGRATION_BRANCH,
    TEST_05_MIGRATION_BRANCH,
)
from migration_fixer.tests.management.commands._utils import (
    execute_command,
    temporary_checkout,
)


@pytest.mark.env("invalid_repo")
@pytest.mark.django_db
def test_invalid_repo(invalid_git_repo, mocker):
    mocker.patch(
        "django.core.management.commands.makemigrations.Command.handle",
        side_effect=CommandError("Conflicting migrations detected"),
    )
    cmd = Command(repo=invalid_git_repo.api)
    cmd.verbosity = 1

    with pytest.raises(CommandError) as exc_info:
        execute_command(cmd, fix=True)

    assert "Git repository is not yet setup." in str(exc_info.value)


@pytest.mark.env("test_01")
@pytest.mark.django_db
def test_run_makemigrations_is_valid_without_any_conflicts(git_repo):
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_01_MIGRATION_BRANCH,
    ) as target_branch:
        output1 = execute_command(cmd)
        output2 = execute_command(cmd, fix=True)

    assert target_branch.name == TEST_01_MIGRATION_BRANCH
    assert output1 == "No changes detected\n"
    assert output2 == "No changes detected\n"


@pytest.mark.env("test_01")
@pytest.mark.django_db
def test_run_makemigrations_is_valid_without_any_conflicts_verbose(git_repo):
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_01_MIGRATION_BRANCH,
    ) as target_branch:
        output1 = execute_command(cmd, verbosity=2)
        output2 = execute_command(cmd, verbosity=2, fix=True)

    assert target_branch.name == TEST_01_MIGRATION_BRANCH
    assert output1 == "No changes detected\n"
    assert output2 == "No changes detected\n"


@pytest.mark.env("test_02")
@pytest.mark.django_db
def test_run_makemigrations_with_fix_is_valid_for_conflicts(git_repo):
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_02_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(cmd, default_branch=TEST_01_MIGRATION_BRANCH, fix=True)

    assert target_branch.name == TEST_02_MIGRATION_BRANCH
    assert output == f"{cmd.success_msg}\n"


@pytest.mark.env("test_02")
@pytest.mark.django_db
def test_run_makemigrations_with_fix_is_valid_for_conflicts_verbose(git_repo):
    cmd = Command(repo=git_repo.api)
    expected_output = f"""Verifying git repository...
Retrieving the current branch...
Fetching git remote origin changes on: {TEST_01_MIGRATION_BRANCH}
Retrieving the last commit sha on: {TEST_01_MIGRATION_BRANCH}
Retrieving changed files between the current branch and {TEST_01_MIGRATION_BRANCH}
Retrieving the last migration on: {TEST_01_MIGRATION_BRANCH}
Fixing numbered migration...
Updating migration "0002_alter_testmodel_active.py" dependency to 0002_alter_testmodel_age
Renaming migration "0002_alter_testmodel_active.py" to "0003_alter_testmodel_active.py"
Successfully fixed migrations.
"""

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_02_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(
            cmd, default_branch=TEST_01_MIGRATION_BRANCH, verbosity=2, fix=True
        )

    assert target_branch.name == TEST_02_MIGRATION_BRANCH
    assert output == expected_output


@pytest.mark.env("test_02")
@pytest.mark.django_db
def test_run_makemigrations_with_fix_and_skip_update_is_valid_for_conflicts(git_repo):
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_02_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(
            cmd,
            default_branch=TEST_01_MIGRATION_BRANCH,
            fix=True,
            skip_default_branch_update=True,
        )

    assert target_branch.name == TEST_02_MIGRATION_BRANCH
    assert output == f"{cmd.success_msg}\n"


@pytest.mark.env("test_02")
@pytest.mark.django_db
def test_run_makemigrations_with_fix_and_skip_update_is_valid_for_conflicts_verbose(
    git_repo,
):
    cmd = Command(repo=git_repo.api)
    expected_output = f"""Verifying git repository...
Retrieving the current branch...
Retrieving the last commit sha on: {TEST_01_MIGRATION_BRANCH}
Retrieving changed files between the current branch and {TEST_01_MIGRATION_BRANCH}
Retrieving the last migration on: {TEST_01_MIGRATION_BRANCH}
Fixing numbered migration...
Updating migration "0002_alter_testmodel_active.py" dependency to 0002_alter_testmodel_age
Renaming migration "0002_alter_testmodel_active.py" to "0003_alter_testmodel_active.py"
Successfully fixed migrations.
"""

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_02_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(
            cmd,
            default_branch=TEST_01_MIGRATION_BRANCH,
            verbosity=2,
            fix=True,
            skip_default_branch_update=True,
        )

    assert target_branch.name == TEST_02_MIGRATION_BRANCH
    assert output == expected_output


@pytest.mark.env("test_03")
@pytest.mark.django_db
def test_run_makemigrations_with_fix_is_valid_for_multiple_file_conflicts(git_repo):
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_03_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(cmd, default_branch=TEST_01_MIGRATION_BRANCH, fix=True)

    assert target_branch.name == TEST_03_MIGRATION_BRANCH
    assert output == f"{cmd.success_msg}\n"


@pytest.mark.env("test_03")
@pytest.mark.django_db
def test_run_makemigrations_with_fix_is_valid_for_multiple_file_conflicts_verbose(
    git_repo,
):
    cmd = Command(repo=git_repo.api)
    expected_output = f"""Verifying git repository...
Retrieving the current branch...
Fetching git remote origin changes on: {TEST_01_MIGRATION_BRANCH}
Retrieving the last commit sha on: {TEST_01_MIGRATION_BRANCH}
Retrieving changed files between the current branch and {TEST_01_MIGRATION_BRANCH}
Retrieving the last migration on: {TEST_01_MIGRATION_BRANCH}
Fixing numbered migration...
Updating migration "0002_testmodel_created_by.py" dependency to 0002_alter_testmodel_age
Renaming migration "0002_testmodel_created_by.py" to "0003_testmodel_created_by.py"
Updating migration "0003_auto_20210708_1317.py" dependency to 0003_testmodel_created_by
Renaming migration "0003_auto_20210708_1317.py" to "0004_auto_20210708_1317.py"
Successfully fixed migrations.
"""

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_03_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(
            cmd, default_branch=TEST_01_MIGRATION_BRANCH, verbosity=2, fix=True
        )

    assert target_branch.name == TEST_03_MIGRATION_BRANCH
    assert output == expected_output


@pytest.mark.env("test_04")
@pytest.mark.django_db
def test_run_makemigrations_fix_with_an_invalid_module(git_repo):
    expected_output = """Error: Unable to fix migration for "demo" app: testmodel_dob.py
NOTE: It needs to begin with a number. eg. 0001_*
"""
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_04_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(cmd, default_branch=TEST_01_MIGRATION_BRANCH, fix=True)

    assert target_branch.name == TEST_04_MIGRATION_BRANCH
    assert expected_output == output


@pytest.mark.env("test_05")
@pytest.mark.django_db
def test_run_makemigrations_fix_with_mixed_invalid_modules(git_repo):
    expected_output = """Error: Unable to fix migration for "demo" app: custom_migration.py
NOTE: It needs to begin with a number. eg. 0001_*
"""
    cmd = Command(repo=git_repo.api)

    with temporary_checkout(
        git_repo,
        default_branch_name=TEST_01_MIGRATION_BRANCH,
        target_branch_name=TEST_05_MIGRATION_BRANCH,
    ) as target_branch:
        output = execute_command(cmd, default_branch=TEST_01_MIGRATION_BRANCH, fix=True)

    assert target_branch.name == TEST_05_MIGRATION_BRANCH
    assert expected_output == output
