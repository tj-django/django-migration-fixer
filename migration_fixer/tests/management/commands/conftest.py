import os
import pathlib

import pytest
from git import Repo
from pytest_shutil.workspace import Workspace


@pytest.fixture(autouse=True)
def use_demo_app(settings):
    settings.INSTALLED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "migration_fixer",
        "migration_fixer.tests.demo",
    ]


class GitRepo(Workspace):
    def __init__(self, workspace, delete=False):
        super(GitRepo, self).__init__(workspace, delete)
        self.api = Repo.init(self.workspace)
        self.uri = "file://%s" % self.workspace


@pytest.fixture
def git_repo(settings):
    workspace = pathlib.Path(
        os.path.join(settings.BASE_DIR, "migration_fixer", "tests", "demo")
    )

    with GitRepo(workspace=workspace) as repo:
        yield repo


@pytest.fixture
def invalid_git_repo(settings):
    workspace = os.path.join(settings.BASE_DIR, "non_existing")

    with GitRepo(workspace=workspace, delete=True) as repo:
        yield repo
