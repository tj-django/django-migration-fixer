"""Tests for `migration_fixer` package."""

from django.test import override_settings

from migration_fixer.management.commands.makemigrations import Command
from migration_fixer.tests.base import BaseCommandTestCase


@override_settings(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "migration_fixer",
        "migration_fixer.tests.demo",
    ]
)
class MigrationFixerTestCase(BaseCommandTestCase):
    cmd_class = Command
    expected_output = Command.success_msg

    def test_equal(self):
        self.assertEqual(1, 1)
