from django.utils import translation

from migration_fixer.utils import (
    _clean_message,
    _decode_message,
    no_translations,
    run_command,
)


def test__clean_message():
    message = "New\n\rTest\n\r"
    expected_output = "New\n\rTest"

    current_output = _clean_message(message)

    assert expected_output == current_output


def test__decode_message():
    encoding = "utf-8"
    message = b"\xe2\x86\x92"
    expected_output = "→"

    current_output = _decode_message(message, encoding)

    assert expected_output == current_output


def test_no_translations():
    @no_translations
    def do_not_translate():
        assert translation.get_language() is None

    do_not_translate()


def test_run_command():
    head_sha_has_no_error, head_sha_output, head_sha_error = run_command(
        "git rev-parse HEAD"
    )

    assert head_sha_has_no_error is True
    assert head_sha_output != ""
    assert head_sha_error == ""
