import ctypes.util
import sys
from enum import Enum
from typing import *
from ctypes import *


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
        raise TypeError(f"Input must be a string or bytes")
    return string


libname = ctypes.util.find_library("econf")
libeconf = CDLL(libname)


def set_value(kf: c_void_p, group: str, key: str, value: Any) -> Econf_err:
    if isinstance(value, int):
        res = set_int64_value(kf, group, key, value)
    elif isinstance(value, float):
        res = set_double_value(kf, group, key, value)
    elif isinstance(value, str):
        res = set_string_value(kf, group, key, value)
    elif isinstance(value, bool):
        res = set_bool_value(kf, group, key, value)
    else:
        raise TypeError(f"\"value\" parameter is not one of the supported types")
    return res


def read_file(file_name: str, delim: str, comment: str) -> c_void_p:
    # return Pointer to object, no need to parse it
    result = c_void_p(None)
    file_name = _encode_str(file_name)
    delim = _encode_str(delim)
    comment = _encode_str(comment)
    err = libeconf.econf_readFile(byref(result), file_name, delim, comment)
    if err != 0:
        raise _exceptions(err, f"read_file failed with error: {err_string(err)}")
    return result


def merge_files(usr_file: c_void_p, etc_file: c_void_p) -> c_void_p:
    merged_file = c_void_p(None)
    err = libeconf.econf_mergeFiles(byref(merged_file), usr_file, etc_file)
    if err != 0:
        raise _exceptions(err, f"merge_files failed with error: {err_string(err)}")
    return merged_file


# this reads either the first OR the second file if the first one does not exist
def read_dirs(
    usr_conf_dir: str,
    etc_conf_dir: str,
    project_name: str,
    config_suffix: str,
    delim: str,
    comment: str,
) -> c_void_p:
    result = c_void_p(None)
    c_usr_conf_dir = c_char_p(_encode_str(usr_conf_dir))
    c_etc_conf_dir = c_char_p(_encode_str(etc_conf_dir))
    c_project_name = c_char_p(_encode_str(project_name))
    c_config_suffix = c_char_p(_encode_str(config_suffix))
    err = libeconf.econf_readDirs(
        byref(result),
        c_usr_conf_dir,
        c_etc_conf_dir,
        c_project_name,
        c_config_suffix,
        delim,
        comment,
    )
    if err != 0:
        raise _exceptions(err, f"read_dirs failed with error: {err_string(err)}")
    return result


# this reads either the first OR the second file if the first one does not exist
def read_dirs_history(
    usr_conf_dir: str,
    etc_conf_dir: str,
    project_name: str,
    config_suffix: str,
    delim: str,
    comment: str,
) -> list[c_void_p]:
    key_files = c_void_p(None)
    c_size = c_size_t()
    c_usr_conf_dir = c_char_p(_encode_str(usr_conf_dir))
    c_etc_conf_dir = c_char_p(_encode_str(etc_conf_dir))
    c_project_name = c_char_p(_encode_str(project_name))
    c_config_suffix = c_char_p(_encode_str(config_suffix))
    err = libeconf.econf_readDirsHistory(
        byref(key_files),
        byref(c_size),
        c_usr_conf_dir,
        c_etc_conf_dir,
        c_project_name,
        c_config_suffix,
        delim,
        comment,
    )
    if err != 0:
        raise _exceptions(
            err, f"read_dirs_history failed with error: {err_string(err)}"
        )
    arr = cast(key_files, POINTER(c_void_p * c_size.value))
    result = [c_void_p(i) for i in arr.contents]
    return result


def new_key_file(delim: str, comment: str) -> c_void_p:
    result = c_void_p(None)
    delim = _encode_str(delim)
    comment = _encode_str(comment)
    err = libeconf.econf_newKeyFile(result, delim, comment)
    if err != 0:
        raise _exceptions(err, f"new_key_file failed with error: {err_string(err)}")
    return result


def new_ini_file() -> c_void_p:
    result = c_void_p(None)
    err = libeconf.econf_newIniFile(result)
    if err != 0:
        raise _exceptions(err, f"new_ini_file failed with error: {err_string(err)}")
    return result


def write_file(kf: c_void_p, save_to_dir: str, file_name: str) -> Econf_err:
    c_save_to_dir = c_char_p(_encode_str(save_to_dir))
    c_file_name = c_char_p(_encode_str(file_name))
    err = libeconf.econf_writeFile(byref(kf), c_save_to_dir, c_file_name)
    return Econf_err(err)


def get_path(kf: c_void_p) -> str:
    # extract from pointer
    libeconf.econf_getPath.restype = c_char_p
    return libeconf.econf_getPath(kf).decode("utf-8")


def get_groups(kf: c_void_p) -> list[str]:
    c_length = c_size_t()
    c_groups = c_void_p(None)
    err = libeconf.econf_getGroups(kf, byref(c_length), byref(c_groups))
    if err != 0:
        _exceptions(err, f"get_groups failed with error: {err_string(err)}")
    arr = cast(c_groups, POINTER(c_char_p * c_length.value))
    result = [i.decode("utf-8") for i in arr.contents]
    return result


# Not passing a group currently leads to ECONF_NOKEY error
def get_keys(kf: c_void_p, group: str) -> list[str]:
    c_length = c_size_t()
    c_keys = c_void_p(None)
    group = _encode_str(group)
    err = libeconf.econf_getKeys(kf, group, byref(c_length), byref(c_keys))
    if err != 0:
        _exceptions(err, f"get_keys failed with error: {err_string(err)}")
    arr = cast(c_keys, POINTER(c_char_p * c_length.value))
    result = [i.decode("utf-8") for i in arr.contents]
    return result


def get_int_value(kf: c_void_p, group: str, key: str) -> int:
    return get_int64_value(kf, group, key)


def get_int64_value(kf: c_void_p, group: str, key: str) -> int:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_int64()
    err = libeconf.econf_getInt64Value(kf, c_group, c_key, byref(c_result))
    if err != 0:
        _exceptions(err, f"get_int64_value failed with error: {err_string(err)}")
    return c_result.value


def get_uint_value(kf: c_void_p, group: str, key: str) -> int:
    return get_uint64_value(kf, group, key)


def get_uint64_value(kf: c_void_p, group: str, key: str) -> int:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_uint64()
    err = libeconf.econf_getUInt64Value(kf, c_group, c_key, byref(c_result))
    if err != 0:
        _exceptions(err, f"get_uint64_value failed with error: {err_string(err)}")
    return c_result.value


def get_float_value(kf: c_void_p, group: str, key: str) -> float:
    return get_double_value(kf, group, key)


def get_double_value(kf: c_void_p, group: str, key: str) -> float:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_double()
    err = libeconf.econf_getDoubleValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        _exceptions(err, f"get_double_value failed with error: {err_string(err)}")
    return c_result.value


def get_string_value(kf: c_void_p, group: str, key: str) -> str:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_char_p()
    err = libeconf.econf_getStringValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        _exceptions(err, f"get_string_value failed with error: {err_string(err)}")
    return c_result.value.decode("utf-8")


def get_bool_value(kf: c_void_p, group: str, key: str) -> bool:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_bool()
    err = libeconf.econf_getBoolValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        _exceptions(err, f"get_bool_value failed with error: {err_string(err)}")
    return c_result.value


def get_int_value_def(kf: c_void_p, group: str, key: str, default: int) -> int:
    return get_int64_value_def(kf, group, key, default)


def get_int64_value_def(kf: c_void_p, group: str, key: str, default: int) -> int:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_int64()
    if not isinstance(default, int):
        raise TypeError(f"\"default\" parameter must be of type int")
    c_default = c_int64(default)
    err = libeconf.econf_getInt64ValueDef(
        kf, c_group, c_key, byref(c_result), c_default
    )
    if err != 0:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_int64_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_uint_value_def(kf: c_void_p, group: str, key: str, default: int) -> int:
    return get_uint64_value_def(kf, group, key, default)


def get_uint64_value_def(kf: c_void_p, group: str, key: str, default: int) -> int:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_uint64()
    if not isinstance(default, int) | (default < 0):
        raise TypeError(f"\"default\" parameter must be of type int and greater or equal to zero")
    c_default = c_uint64(default)
    err = libeconf.econf_getUInt64ValueDef(
        kf, c_group, c_key, byref(c_result), c_default
    )
    if err != 0:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_uint64_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_float_value_def(kf: c_void_p, group: str, key: str, default: float) -> float:
    return get_double_value_def(kf, group, key, default)


def get_double_value_def(kf: c_void_p, group: str, key: str, default: float) -> float:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_double()
    if not isinstance(default, float):
        raise TypeError(f"\"default\" parameter must be of type float")
    c_default = c_double(default)
    err = libeconf.econf_getDoubleValueDef(
        kf, c_group, c_key, byref(c_result), c_default
    )
    if err != 0:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_double_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_string_value_def(kf: c_void_p, group: str, key: str, default: str) -> str:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_char_p()
    c_default = c_char_p(_encode_str(default))
    err = libeconf.econf_getStringValueDef(
        kf, c_group, c_key, byref(c_result), c_default
    )
    if err != 0:
        if err == 5:
            return c_default.value.decode("utf-8")
        _exceptions(err, f"get_string_value_def failed with error: {err_string(err)}")
    return c_result.value.decode("utf-8")


def get_bool_value_def(kf: c_void_p, group: str, key: str, default: bool) -> bool:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_result = c_bool()
    if not isinstance(default, bool):
        raise TypeError(f"\"value\" parameter must be of type bool")
    c_default = c_bool(default)
    err = libeconf.econf_getBoolValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_bool_value_def failed with error: {err_string(err)}")
    return c_result.value


def set_int_value(kf: c_void_p, group: str, key: str, value: int) -> Econf_err:
    return set_int64_value(kf, group, key, value)


def set_int64_value(kf: c_void_p, group: str, key: str, value: int) -> Econf_err:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    if not isinstance(value, int):
        raise TypeError(f"\"value\" parameter must be of type int")
    c_value = c_int64(value)
    err = libeconf.econf_setInt64Value(kf, c_group, c_key, c_value)
    if err != 0:
        _exceptions(err, f"set_int64_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_uint_value(kf: c_void_p, group: str, key: str, value: int) -> Econf_err:
    return set_uint64_value(kf, group, key, value)


def set_uint64_value(kf: c_void_p, group: str, key: str, value: int) -> Econf_err:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    if not isinstance(value, int) | (value < 0):
        raise TypeError(f"\"value\" parameter must be of type int and be greater or equal to zero")
    c_value = c_uint64(value)
    err = libeconf.econf_setUInt64Value(kf, c_group, c_key, c_value)
    if err != 0:
        _exceptions(err, f"set_uint64_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_float_value(kf: c_void_p, group: str, key: str, value: float) -> Econf_err:
    return set_double_value(kf, group, key, value)


def set_double_value(kf: c_void_p, group: str, key: str, value: float) -> Econf_err:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    if not isinstance(value, float):
        raise TypeError(f"\"value\" parameter must be of type float")
    c_value = c_double(value)
    err = libeconf.econf_setDoubleValue(kf, c_group, c_key, c_value)
    if err != 0:
        _exceptions(err, f"set_double_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_string_value(kf: c_void_p, group: str, key: str, value: str) -> Econf_err:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    c_value = c_char_p(_encode_str(value))
    err = libeconf.econf_setStringValue(kf, c_group, c_key, c_value)
    if err != 0:
        _exceptions(err, f"set_string_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_bool_value(kf: c_void_p, group: str, key: str, value: bool) -> Econf_err:
    c_group = c_char_p(_encode_str(group))
    c_key = c_char_p(_encode_str(key))
    if not isinstance(value, bool):
        raise TypeError(f"\"value\" parameter must be of type bool")
    c_value = c_bool(value)
    err = libeconf.econf_setBoolValue(kf, c_group, c_key, c_value)
    if err != 0:
        _exceptions(err, f"set_bool_value failed with error: {err_string(err)}")
    return Econf_err(err)


def err_string(error: int):
    if not isinstance(error, int):
        raise TypeError("Error codes must be of type int")
    c_int(error)
    libeconf.econf_errString.restype = c_char_p
    return libeconf.econf_errString(error).decode("utf-8")


def err_location(filename: str, line_nr: int):
    c_filename = c_char_p(_encode_str(filename))
    c_line_nr = c_uint64(line_nr)
    libeconf.econf_errLocation(byref(c_filename), byref(c_line_nr))
    return c_filename.value, c_line_nr.value


def free_file(kf):
    libeconf.econf_freeFile(kf)
    return
