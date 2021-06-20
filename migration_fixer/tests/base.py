import abc
from io import StringIO
from typing import Type

from django.core.management import BaseCommand, call_command
from django.test import TestCase
from six import with_metaclass


class BaseCommandTestCase(with_metaclass(abc.ABCMeta, TestCase)):
    cmd_class: Type[BaseCommand]
    expected_output: str
    base_kwargs = {"verbosity": 0}

    @classmethod
    def setup_command(cls, *args, **kwargs):
        cmd = cls.cmd_class()

        out = StringIO()

        kwargs["stdout"] = out
        kwargs.update(cls.base_kwargs)

        call_command(cmd, *args, **kwargs)

        output = out.getvalue()

        if cls.expected_output is not None and cls.expected_output not in output:
            raise AssertionError(
                f"Expected: {repr(cls.expected_output)} != {repr(output)}",
            )
