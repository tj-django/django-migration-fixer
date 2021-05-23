import abc
from io import StringIO

from six import with_metaclass

from django.core.management import BaseCommand, call_command
from django.test import TestCase


class BaseCommandTestCase(with_metaclass(abc.ABCMeta, TestCase)):
    cmd_class = None
    cmd_name = None
    expected_output = None
    base_kwargs = {"verbosity": 0}

    @classmethod
    @abc.abstractmethod
    def setup_command_data(cls, *arg, **kwargs):
        pass

    @classmethod
    def setup_command(cls, *args, **kwargs):
        cmd = cls.cmd_name

        if cls.cmd_class is not None and issubclass(cls.cmd_class, BaseCommand):
            cmd = cls.cmd_class()

        if cmd is not None:
            out = StringIO()

            kwargs["stdout"] = out
            kwargs.update(cls.base_kwargs)

            call_command(cmd, *args, **kwargs)

            output = out.getvalue()

            if cls.expected_output is not None and cls.expected_output not in output:
                raise AssertionError(
                    f"Expected: {repr(cls.expected_output)} != {repr(output)}",
                )
