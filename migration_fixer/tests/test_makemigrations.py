"""Tests for `migration_fixer` package."""

from django.test import override_settings

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
    @classmethod
    def setup_command_data(cls, *arg, **kwargs):
        pass

    def test_equal(self):
        self.assertEqual(1, 1)
