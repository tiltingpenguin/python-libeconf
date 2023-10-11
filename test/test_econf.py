import pytest
import econf
from contextlib import contextmanager
from pathlib import Path


FILE = econf.read_file("examples/example.conf", "=", "#")
FILE2 = econf.read_file("examples/example2.conf", "=", "#")


@contextmanager
def does_not_raise():
    yield

@pytest.mark.parametrize("value,expected,context", [("foo", b"foo", does_not_raise()), (b"foo", b"foo", does_not_raise()), (5, b"", pytest.raises(TypeError))])
def test_encode_str(value, expected, context):
    with context:
        assert econf._encode_str(value) == expected


@pytest.mark.parametrize("value,expected,context", [(5, True, does_not_raise()), (99999999999999999999, False, does_not_raise()), ("a", False, pytest.raises(TypeError))])
def test_check_int_overflow(value, expected, context):
    with context:
        result = econf._check_int_overflow(value)
        assert result == expected


@pytest.mark.parametrize("value,expected,context", [(5, True, does_not_raise()), (99999999999999999999, False, does_not_raise()), ("a", False, pytest.raises(TypeError))])
def test_check_uint_overflow(value, expected, context):
    with context:
        result = econf._check_uint_overflow(value)
        assert result == expected

@pytest.mark.skip
@pytest.mark.parametrize("value,expected,context", [(5.5, True, does_not_raise()), (99999999999999999999.1, False, does_not_raise()), ("a", False, pytest.raises(TypeError))])
def test_check_float_overflow(value, expected, context):
    with context:
        result = econf._check_float_overflow(value)
        assert result == expected


def test_read_file():
    file = "examples/example.conf"
    delim = "="
    comment = "#"

    ef = econf.read_file(file, delim, comment)

    assert ef._ptr != None


def test_new_key_file():
    result = econf.new_key_file('=', '#')

    assert result
    assert type(result) == econf.EconfFile


def test_new_ini_file():
    result = econf.new_ini_file()

    assert result
    assert type(result) == econf.EconfFile


def test_merge_files():
    result = econf.merge_files(FILE, FILE2)

    assert len(econf.get_keys(result, None)) == 2
    assert len(econf.get_groups(result)) == 3

@pytest.mark.skip
def test_read_dirs():
    pass


@pytest.mark.skip
def test_read_dirs_history():
    pass


def test_write_file(tmp_path):
    d = str(tmp_path)
    name = "example.conf"
    result = econf.write_file(FILE, d, name)

    assert (tmp_path / "example.conf").exists()



@pytest.mark.parametrize("file,context,example", [(FILE, does_not_raise(), ["Another Group", "First Group", "Group"]), (FILE2, pytest.raises(KeyError), [])])
def test_get_groups(file, context, example):
    with context:
        assert econf.get_groups(file) == example


@pytest.mark.parametrize("file,group,expected", [(FILE, b"Group", 3), (FILE2, None, 2)])
def test_get_keys(file, group, expected):
    result = econf.get_keys(file, group)

    assert len(result) == expected
