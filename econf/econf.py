"""
Econf provides functionality for interacting with Key-Value config files, like getting and setting values for read config files.

For more information please have a look at the API
"""
import ctypes.util
from enum import Enum
from dataclasses import dataclass
from typing import *
from ctypes import *

LIBNAME = ctypes.util.find_library("econf")
LIBECONF = CDLL(LIBNAME)


@dataclass
class EconfFile:
    """
    Class which points to the Key Value storage object
    """

    __ptr: c_void_p

    def __del__(self):
        free_file(self)


class Econf_err(Enum):
    ECONF_SUCCESS = 0
    ECONF_ERROR = 1
    ECONF_NOMEM = 2
    ECONF_NOFILE = 3
    ECONF_NOGROUP = 4
    ECONF_NOKEY = 5
    ECONF_EMPTYKEY = 6
    ECONF_WRITEERROR = 7
    ECONF_PARSE_ERROR = 8
    ECONF_MISSING_BRACKET = 9
    ECONF_MISSING_DELIMITER = 10
    ECONF_EMPTY_SECTION_NAME = 11
    ECONF_TEXT_AFTER_SECTION = 12
    ECONF_FILE_LIST_IS_NULL = 13
    ECONF_WRONG_BOOLEAN_VALUE = 14
    ECONF_KEY_HAS_NULL_VALUE = 15
    ECONF_WRONG_OWNER = 16
    ECONF_WRONG_GROUP = 17
    ECONF_WRONG_FILE_PERMISSION = 18
    ECONF_WRONG_DIR_PERMISSION = 19
    ECONF_ERROR_FILE_IS_SYM_LINK = 20
    ECONF_PARSING_CALLBACK_FAILED = 21


def _exceptions(err: int, val: str):
    if err == 1:
        raise Exception(val)
    elif err == 2:
        raise MemoryError(val)
    elif err == 3:
        raise FileNotFoundError(val)
    elif err == 4:
        raise KeyError(val)
    elif err == 5:
        raise KeyError(val)
    elif err == 6:
        raise KeyError(val)
    elif err == 7:
        raise OSError(val)
    elif err == 8:
        raise Exception(val)
    elif err == 9:
        raise SyntaxError(val)
    elif err == 10:
        raise SyntaxError(val)
    elif err == 11:
        raise SyntaxError(val)
    elif err == 12:
        raise SyntaxError(val)
    elif err == 13:
        raise ValueError(val)
    elif err == 14:
        raise ValueError(val)
    elif err == 15:
        raise ValueError(val)
    elif err == 16:
        raise PermissionError(val)
    elif err == 17:
        raise PermissionError(val)
    elif err == 18:
        raise PermissionError(val)
    elif err == 19:
        raise PermissionError(val)
    elif err == 20:
        raise FileNotFoundError(val)
    elif err == 21:
        raise Exception(val)
    else:
        raise Exception(val)


def _encode_str(string: str | bytes) -> bytes:
    if isinstance(string, str):
        string = string.encode("utf-8")
    elif not isinstance(string, bytes):
        raise TypeError("Input must be a string or bytes")
    return string


def _check_int_overflow(val: int) -> bool:
    if isinstance(val, int):
        c_val = c_int64(val)
        return c_val.value == val
    else:
        raise TypeError("parameter is not an integer")


def _check_uint_overflow(val: int) -> bool:
    if isinstance(val, int) & (val >= 0):
        c_val = c_uint64(val)
        return c_val.value == val
    else:
        raise TypeError("parameter is not a unsigned integer")


def _check_float_overflow(val: float) -> bool:
    if isinstance(val, float):
        c_val = c_double(val)
        return c_val.value == val
    else:
        raise TypeError("parameter is not a float")


def set_value(
    ef: EconfFile, group: str | bytes, key: str | bytes, value: Any
) -> Econf_err:
    """
    Dynamically set a value in a keyfile and returns a status code

    :param ef: EconfFile object to set value in
    :param group: group of the key to be changed
    :param key: key to be changed
    :param value: desired value
    :return: Error code
    """
    if isinstance(value, int):
        if value >= 0:
            res = set_uint_value(ef, group, key, value)
        else:
            res = set_int_value(ef, group, key, value)
    elif isinstance(value, float):
        res = set_float_value(ef, group, key, value)
    elif isinstance(value, str) | isinstance(value, bytes):
        res = set_string_value(ef, group, key, value)
    elif isinstance(value, bool):
        res = set_bool_value(ef, group, key, value)
    else:
        raise TypeError("'value' parameter is not one of the supported types")
    return res


def read_file(
    file_name: str | bytes, delim: str | bytes, comment: str | bytes
) -> EconfFile:
    """
    Read a config file and write the key-value pairs into a keyfile object

    :param file_name: absolute path of file to be parsed
    :param delim: delimiter of a key/value e.g. '='
    :param comment: string that defines the start of a comment e.g. '#'
    :return: Key-Value storage object
    """
    result = EconfFile(c_void_p(None))
    file_name = _encode_str(file_name)
    delim = _encode_str(delim)
    comment = _encode_str(comment)
    err = LIBECONF.econf_readFile(
        byref(result._EconfFile__ptr), file_name, delim, comment
    )
    if err:
        raise _exceptions(err, f"read_file failed with error: {err_string(err)}")
    return result


def merge_files(usr_file: EconfFile, etc_file: EconfFile) -> EconfFile:
    """
    Merge the content of 2 keyfile objects

    :param usr_file: first EconfFile object
    :param etc_file: second EconfFile object
    :return: merged EconfFile object
    """
    merged_file = EconfFile(c_void_p())
    err = LIBECONF.econf_mergeFiles(
        byref(merged_file._EconfFile__ptr),
        usr_file._EconfFile__ptr,
        etc_file._EconfFile__ptr,
    )
    if err:
        raise _exceptions(err, f"merge_files failed with error: {err_string(err)}")
    return merged_file


# this reads either the first OR the second file if the first one does not exist
def read_dirs(
    usr_conf_dir: str | bytes,
    etc_conf_dir: str | bytes,
    project_name: str | bytes,
    config_suffix: str | bytes,
    delim: str | bytes,
    comment: str | bytes,
) -> EconfFile:
    """
    Read configuration from the first found config file and merge with snippets from conf.d/ directory

    e.g. searches /usr/etc/ and /etc/ for an example.conf file and merges it with the snippets in either
    /usr/etc/example.conf.d/ or /etc/example.conf.d

    :param usr_conf_dir: absolute path of the first directory to be searched
    :param etc_conf_dir: absolute path of the second directory to be searched
    :param project_name: basename of the configuration file
    :param config_suffix: suffix of the configuration file
    :param delim: delimiter of a key/value e.g. '='
    :param comment: string that defines the start of a comment e.g. '#'
    :return: merged EconfFile object
    """
    result = EconfFile(c_void_p())
    c_usr_conf_dir = _encode_str(usr_conf_dir)
    c_etc_conf_dir = _encode_str(etc_conf_dir)
    c_project_name = _encode_str(project_name)
    c_config_suffix = _encode_str(config_suffix)
    err = LIBECONF.econf_readDirs(
        byref(result._EconfFile__ptr),
        c_usr_conf_dir,
        c_etc_conf_dir,
        c_project_name,
        c_config_suffix,
        delim,
        comment,
    )
    if err:
        raise _exceptions(err, f"read_dirs failed with error: {err_string(err)}")
    return result


# this reads either the first OR the second file if the first one does not exist
def read_dirs_history(
    usr_conf_dir: str | bytes,
    etc_conf_dir: str | bytes,
    project_name: str | bytes,
    config_suffix: str | bytes,
    delim: str | bytes,
    comment: str | bytes,
) -> list[EconfFile]:
    """
    Read configuration from the first found config file and snippets from conf.d/ directory

    e.g. searches /usr/etc/ and /etc/ for an example.conf file and the snippets in either
    /usr/etc/example.conf.d/ or /etc/example.conf.d

    :param usr_conf_dir: absolute path of the first directory to be searched
    :param etc_conf_dir: absolute path of the second directory to be searched
    :param project_name: basename of the configuration file
    :param config_suffix: suffix of the configuration file
    :param delim: delimiter of a key/value e.g. '='
    :param comment: string that defines the start of a comment e.g. '#'
    :return: list of EconfFile objects
    """
    key_files = c_void_p(None)
    c_size = c_size_t()
    c_usr_conf_dir = _encode_str(usr_conf_dir)
    c_etc_conf_dir = _encode_str(etc_conf_dir)
    c_project_name = _encode_str(project_name)
    c_config_suffix = _encode_str(config_suffix)
    err = LIBECONF.econf_readDirsHistory(
        byref(key_files),
        byref(c_size),
        c_usr_conf_dir,
        c_etc_conf_dir,
        c_project_name,
        c_config_suffix,
        delim,
        comment,
    )
    if err:
        raise _exceptions(
            err, f"read_dirs_history failed with error: {err_string(err)}"
        )
    arr = cast(key_files, POINTER(c_void_p * c_size.value))
    result = [EconfFile(c_void_p(i)) for i in arr.contents]
    return result


def new_key_file(delim: str | bytes, comment: str | bytes) -> EconfFile:
    """
    Create a new empty keyfile

    :param delim: delimiter of a key/value e.g. '='
    :param comment: string that defines the start of a comment e.g. '#'
    :return: created EconfFile object
    """
    result = EconfFile(c_void_p)
    delim = _encode_str(delim)
    comment = _encode_str(comment)
    err = LIBECONF.econf_newKeyFile(byref(result._EconfFile__ptr), delim, comment)
    if err:
        raise _exceptions(err, f"new_key_file failed with error: {err_string(err)}")
    return result


def new_ini_file() -> EconfFile:
    """
    Create a new empty keyfile with delimiter '=' and comment '#'

    :return: created EconfFile object
    """
    result = EconfFile(c_void_p())
    err = LIBECONF.econf_newIniFile(byref(result._EconfFile__ptr))
    if err:
        raise _exceptions(err, f"new_ini_file failed with error: {err_string(err)}")
    return result


def write_file(ef: EconfFile, save_to_dir: str, file_name: str) -> Econf_err:
    """
    Write content of a keyfile to specified location

    :param ef: Key-Value storage object
    :param save_to_dir: directory into which the file has to be written
    :param file_name: filename with suffix of the to be written file
    :return: Error code
    """
    c_save_to_dir = _encode_str(save_to_dir)
    c_file_name = _encode_str(file_name)
    err = LIBECONF.econf_writeFile(
        byref(ef._EconfFile__ptr), c_save_to_dir, c_file_name
    )
    return Econf_err(err)


def get_path(ef: EconfFile) -> str:
    """
    Get the path of the source of the given key file

    :param ef: Key-Value storage object
    :return: path of the config file as string
    """
    # extract from pointer
    LIBECONF.econf_getPath.restype = c_char_p
    return LIBECONF.econf_getPath(ef._EconfFile__ptr).decode("utf-8")


def get_groups(ef: EconfFile) -> list[str]:
    """
    List all the groups of given keyfile

    :param ef: Key-Value storage object
    :return: list of groups in the keyfile
    """
    c_length = c_size_t()
    c_groups = c_void_p(None)
    err = LIBECONF.econf_getGroups(ef._EconfFile__ptr, byref(c_length), byref(c_groups))
    if err:
        _exceptions(err, f"get_groups failed with error: {err_string(err)}")
    arr = cast(c_groups, POINTER(c_char_p * c_length.value))
    result = [i.decode("utf-8") for i in arr.contents]
    return result


# Not passing a group currently leads to ECONF_NOKEY error
def get_keys(ef: EconfFile, group: str) -> list[str]:
    """
    List all the keys of a given group or all keys in a keyfile

    :param ef: Key-Value storage object
    :param group: group of the keys to be returned
    :return: list of keys in the given group
    """
    c_length = c_size_t()
    c_keys = c_void_p(None)
    group = _encode_str(group)
    err = LIBECONF.econf_getKeys(
        ef._EconfFile__ptr, group, byref(c_length), byref(c_keys)
    )
    if err:
        _exceptions(err, f"get_keys failed with error: {err_string(err)}")
    arr = cast(c_keys, POINTER(c_char_p * c_length.value))
    result = [i.decode("utf-8") for i in arr.contents]
    return result


def get_int_value(ef: EconfFile, group: str, key: str) -> int:
    """
    Return an integer value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_int64()
    err = LIBECONF.econf_getInt64Value(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result)
    )
    if err:
        _exceptions(err, f"get_int64_value failed with error: {err_string(err)}")
    return c_result.value


def get_uint_value(ef: EconfFile, group: str, key: str) -> int:
    """
    Return an unsigned integer value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_uint64()
    err = LIBECONF.econf_getUInt64Value(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result)
    )
    if err:
        _exceptions(err, f"get_uint64_value failed with error: {err_string(err)}")
    return c_result.value


def get_float_value(ef: EconfFile, group: str, key: str) -> float:
    """
    Return a float value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_double()
    err = LIBECONF.econf_getDoubleValue(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result)
    )
    if err:
        _exceptions(err, f"get_double_value failed with error: {err_string(err)}")
    return c_result.value


def get_string_value(ef: EconfFile, group: str, key: str) -> str:
    """
    Return a string value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_char_p()
    err = LIBECONF.econf_getStringValue(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result)
    )
    if err:
        _exceptions(err, f"get_string_value failed with error: {err_string(err)}")
    return c_result.value.decode("utf-8")


def get_bool_value(ef: EconfFile, group: str, key: str) -> bool:
    """
    Return a boolean value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_bool()
    err = LIBECONF.econf_getBoolValue(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result)
    )
    if err:
        _exceptions(err, f"get_bool_value failed with error: {err_string(err)}")
    return c_result.value


def get_int_value_def(ef: EconfFile, group: str, key: str, default: int) -> int:
    """
    Return an integer value for given group/key or return a default value if key is not found

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_int64()
    if not isinstance(default, int):
        raise TypeError(f'"default" parameter must be of type int')
    if not _check_int_overflow(default):
        raise ValueError(
            f"Integer overflow found, only up to 64 bit integers are supported"
        )
    c_default = c_int64(default)
    err = LIBECONF.econf_getInt64ValueDef(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_int64_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_uint_value_def(ef: EconfFile, group: str, key: str, default: int) -> int:
    """
    Return an unsigned integer value for given group/key or return a default value if key is not found

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_uint64()
    if not isinstance(default, int) | (default < 0):
        raise TypeError(
            f'"default" parameter must be of type int and greater or equal to zero'
        )
    if not _check_uint_overflow(default):
        raise ValueError(
            f"Integer overflow found, only up to 64 bit unsigned integers are supported"
        )
    c_default = c_uint64(default)
    err = LIBECONF.econf_getUInt64ValueDef(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_uint64_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_float_value_def(ef: EconfFile, group: str, key: str, default: float) -> float:
    """
    Return a float value for given group/key or return a default value if key is not found

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_double()
    if not isinstance(default, float):
        raise TypeError(f'"default" parameter must be of type float')
    if not _check_float_overflow(default):
        raise ValueError(
            f"Float overflow found, only up to 64 bit floats are supported"
        )
    c_default = c_double(default)
    err = LIBECONF.econf_getDoubleValueDef(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_double_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_string_value_def(ef: EconfFile, group: str, key: str, default: str) -> str:
    """
    Return a string value for given group/key or return a default value if key is not found

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_char_p()
    c_default = _encode_str(default)
    err = LIBECONF.econf_getStringValueDef(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.decode("utf-8")
        _exceptions(err, f"get_string_value_def failed with error: {err_string(err)}")
    return c_result.value.decode("utf-8")


def get_bool_value_def(ef: EconfFile, group: str, key: str, default: bool) -> bool:
    """
    Return a boolean value for given group/key or return a default value if key is not found

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_bool()
    if not isinstance(default, bool):
        raise TypeError(f'"value" parameter must be of type bool')
    c_default = c_bool(default)
    err = LIBECONF.econf_getBoolValueDef(
        ef._EconfFile__ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_bool_value_def failed with error: {err_string(err)}")
    return c_result.value


def set_int_value(ef: EconfFile, group: str, key: str, value: int) -> Econf_err:
    """
    Setting an integer value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, int):
        raise TypeError(f'"value" parameter must be of type int')
    if not _check_int_overflow(value):
        raise ValueError(
            f"Integer overflow found, only up to 64 bit integers are supported"
        )
    c_value = c_int64(value)
    err = LIBECONF.econf_setInt64Value(
        byref(ef._EconfFile__ptr), c_group, c_key, c_value
    )
    if err:
        _exceptions(err, f"set_int64_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_uint_value(ef: EconfFile, group: str, key: str, value: int) -> Econf_err:
    """
    Setting an unsigned integer value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, int) | (value < 0):
        raise TypeError(
            f'"value" parameter must be of type int and be greater or equal to zero'
        )
    if not _check_uint_overflow(value):
        raise ValueError(
            f"Integer overflow found, only up to 64 bit unsigned integers are supported"
        )
    c_value = c_uint64(value)
    err = LIBECONF.econf_setUInt64Value(
        byref(ef._EconfFile__ptr), c_group, c_key, c_value
    )
    if err:
        _exceptions(err, f"set_uint64_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_float_value(ef: EconfFile, group: str, key: str, value: float) -> Econf_err:
    """
    Setting a float value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, float):
        raise TypeError(f'"value" parameter must be of type float')
    if not _check_float_overflow(value):
        raise ValueError(
            f"Float overflow found, only up to 64 bit floats are supported"
        )
    c_value = c_double(value)
    err = LIBECONF.econf_setDoubleValue(
        byref(ef._EconfFile__ptr), c_group, c_key, c_value
    )
    if err:
        _exceptions(err, f"set_double_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_string_value(
    ef: EconfFile, group: str, key: str, value: str | bytes
) -> Econf_err:
    """
    Setting a string value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_value = _encode_str(value)
    err = LIBECONF.econf_setStringValue(
        byref(ef._EconfFile__ptr), c_group, c_key, c_value
    )
    if err:
        _exceptions(err, f"set_string_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_bool_value(ef: EconfFile, group: str, key: str, value: bool) -> Econf_err:
    """
    Setting a boolean value for given group/key

    :param ef: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, bool):
        raise TypeError(f'"value" parameter must be of type bool')
    c_value = c_bool(value)
    err = LIBECONF.econf_setBoolValue(
        byref(ef._EconfFile__ptr), c_group, c_key, c_value
    )
    if err:
        _exceptions(err, f"set_bool_value failed with error: {err_string(err)}")
    return Econf_err(err)


def err_string(error: int):
    """
    Convert an error code into error message

    :param error: error code as integer
    :return: error string
    """
    if not isinstance(error, int):
        raise TypeError("Error codes must be of type int")
    c_int(error)
    LIBECONF.econf_errString.restype = c_char_p
    return LIBECONF.econf_errString(error).decode("utf-8")


def err_location():
    """
    Info about the line where an error happened

    :return: path to the last handled file and number of last handled line
    """
    c_filename = c_char_p()
    c_line_nr = c_uint64()
    LIBECONF.econf_errLocation(byref(c_filename), byref(c_line_nr))
    return c_filename.value, c_line_nr.value


def free_file(ef: EconfFile):
    """
    Free the memory of a given keyfile

    :param ef: EconfFile to be freed
    :return: None
    """
    LIBECONF.econf_freeFile(ef._EconfFile__ptr)
    return
