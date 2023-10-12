import pytest
import econf
from contextlib import contextmanager
from pathlib import Path
from ctypes import *


FILE = econf.read_file("examples/example.conf", "=", ";")
FILE2 = econf.read_file("examples/example2.conf", "=", "#")


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "value,expected,context",
    [
        ("foo", b"foo", does_not_raise()),
        (b"foo", b"foo", does_not_raise()),
        (5, b"", pytest.raises(TypeError)),
    ],
)
def test_encode_str(value, expected, context):
    with context:
        assert econf._encode_str(value) == expected


@pytest.mark.parametrize(
    "value,context",
    [
        (5, does_not_raise()),
        (99999999999999999999, pytest.raises(ValueError)),
        ("a", pytest.raises(TypeError)),
    ],
)
def test_ensure_valid_int(value, context):
    with context:
        result = econf._ensure_valid_int(value)

        assert isinstance(result, c_int64)
        assert result.value == value


@pytest.mark.parametrize(
    "value,context",
    [
        (5, does_not_raise()),
        (99999999999999999999, pytest.raises(ValueError)),
        ("a", pytest.raises(TypeError)),
    ],
)
def test_ensure_valid_uint(value, context):
    with context:
        result = econf._ensure_valid_uint(value)

        assert isinstance(result, c_uint64)
        assert result.value >= 0
        assert result.value == value


def test_read_file():
    file = "examples/example.conf"
    delim = "="
    comment = "#"

    ef = econf.read_file(file, delim, comment)

    assert ef._ptr != None


def test_new_key_file():
    result = econf.new_key_file("=", "#")

    assert result
    assert type(result) == econf.EconfFile


def test_new_ini_file():
    result = econf.new_ini_file()

    assert result
    assert type(result) == econf.EconfFile


def test_merge_files():
    result = econf.merge_files(FILE, FILE2)

    assert len(econf.get_keys(result, None)) == 4
    assert len(econf.get_keys(result, "Group")) == 3
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


@pytest.mark.parametrize(
    "file,context,example",
    [
        (FILE, does_not_raise(), ["Another Group", "First Group", "Group"]),
        (FILE2, pytest.raises(KeyError), []),
    ],
)
def test_get_groups(file, context, example):
    with context:
        assert econf.get_groups(file) == example


@pytest.mark.parametrize("file,group,expected", [(FILE, "Group", 3), (FILE2, None, 2)])
def test_get_keys(file, group, expected):
    result = econf.get_keys(file, group)

    assert len(result) == expected


@pytest.mark.parametrize(
    "file,context,group,key,expected",
    [
        (FILE, does_not_raise(), "Group", "Bla", 12311),
        (FILE, pytest.raises(KeyError), "Group", "a", 0),
        (FILE, pytest.raises(KeyError), "a", "Bla", 12311),
        (FILE, does_not_raise(), None, "foo", 6),
        (FILE, does_not_raise(), "Group", "Welcome", 0),
    ],
)
def test_get_int_value(file, context, group, key, expected):
    with context:
        result = econf.get_int_value(file, group, key)

        assert isinstance(result, int)
        assert result == expected


@pytest.mark.parametrize(
    "file,context,group,key,expected",
    [
        (FILE, does_not_raise(), "Group", "Bla", 12311),
        (FILE, pytest.raises(KeyError), "Group", "a", 0),
        (FILE, pytest.raises(KeyError), "a", "Bla", 12311),
        (FILE, does_not_raise(), None, "foo", 6),
        (FILE, does_not_raise(), "Group", "Welcome", 0),
    ],
)
def test_get_uint_value(file, context, group, key, expected):
    with context:
        result = econf.get_uint_value(file, group, key)

        assert isinstance(result, int)
        assert result >= 0
        assert result == expected


@pytest.mark.parametrize(
    "file,context,group,key,expected",
    [
        (FILE, does_not_raise(), "Group", "Bla", 12311),
        (FILE, pytest.raises(KeyError), "Group", "a", 0),
        (FILE, pytest.raises(KeyError), "a", "Bla", 12311),
        (FILE, does_not_raise(), None, "foo", 6.5),
        (FILE, does_not_raise(), "Group", "Welcome", 0),
    ],
)
def test_get_float_value(file, context, group, key, expected):
    with context:
        result = econf.get_float_value(file, group, key)

        assert isinstance(result, float)
        assert result >= 0
        assert result == expected


@pytest.mark.parametrize(
    "file,context,group,key,expected",
    [
        (FILE, does_not_raise(), "Group", "Welcome", "Hello"),
        (FILE, does_not_raise(), "First Group", "Name", "Keys File Example\\tthis value shows\\nescaping"),
        (FILE, does_not_raise(), "First Group", "Welcome[de]", "Hallo"),
        (FILE, does_not_raise(), "Group", "Bla", "12311"),
        (FILE, does_not_raise(), None, "foo", "6.5"),
        (FILE, pytest.raises(KeyError), "a", "Bla", "12311"),
        (FILE, pytest.raises(KeyError), "Group", "foo", "6.5"),
        (FILE, pytest.raises(TypeError), 5, "Bla", "12311")
    ]
)
def test_get_string_value(file, context, group, key, expected):
    with context:
        result = econf.get_string_value(file, group, key)

        assert isinstance(result, str)
        assert result == expected


@pytest.mark.parametrize(
    "file,context,group,key,expected",
    [
        (FILE, does_not_raise(), "Another Group", "Booleans", True),
        (FILE, pytest.raises(Exception, match="Parse error"), "Group", "Bla", True),
        (FILE, pytest.raises(KeyError), "a", "Booleans", True),
        (FILE, pytest.raises(KeyError), "Another Group", "Bools", True)
    ]
)
def test_get_bool_value(file, context, group, key, expected):
    with context:
        result = econf.get_bool_value(file, group, key)

        assert isinstance(result, bool)
        assert result == expected
