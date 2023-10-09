import ctypes.util
from enum import Enum
from typing import *
from ctypes import *

libname = ctypes.util.find_library("econf")
libeconf = CDLL(libname)

@dataclass
class Keyfile:
    """
    Class which points to the Key Value storage object
    """
    ptr: c_void_p

    def __init__(self, ptr: c_void_p):
        self.ptr = ptr

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


def set_value(kf: Keyfile, group: str | bytes, key: str | bytes, value: Any) -> Econf_err:
    """
    Dynamically set a value in a keyfile and returns a status code

    :param kf: Keyfile object to set value in
    :param group: group of the key to be changed
    :param key: key to be changed
    :param value: desired value
    :return: Error code
    """
    if isinstance(value, int):
        if value >= 0:
            res = set_uint_value(kf, group, key, value)
        else:
            res = set_int_value(kf, group, key, value)
    elif isinstance(value, float):
        res = set_float_value(kf, group, key, value)
    elif isinstance(value, str) | isinstance(value, bytes):
        res = set_string_value(kf, group, key, value)
    elif isinstance(value, bool):
        res = set_bool_value(kf, group, key, value)
    else:
        raise TypeError("'value' parameter is not one of the supported types")
    return res


def read_file(file_name: str | bytes, delim: str | bytes, comment: str | bytes) -> Keyfile:
    """
    Read a config file and write the key-value pairs into a keyfile object

    :param file_name: absolute path of file to be parsed
    :param delim: delimiter of a key/value e.g. '='
    :param comment: string that defines the start of a comment e.g. '#'
    :return: Key-Value storage object
    """
    result = Keyfile(c_void_p())
    file_name = _encode_str(file_name)
    delim = _encode_str(delim)
    comment = _encode_str(comment)
    err = libeconf.econf_readFile(byref(result.ptr), file_name, delim, comment)
    if err:
        raise _exceptions(err, f"read_file failed with error: {err_string(err)}")
    return result


def merge_files(usr_file: Keyfile, etc_file: Keyfile) -> Keyfile:
    """
    Merge the content of 2 keyfile objects

    :param usr_file: first Keyfile object
    :param etc_file: second Keyfile object
    :return: merged Keyfile object
    """
    merged_file = Keyfile(c_void_p())
    err = libeconf.econf_mergeFiles(byref(merged_file.ptr), usr_file.ptr, etc_file.ptr)
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
) -> Keyfile:
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
    :return: merged Keyfile object
    """
    result = Keyfile(c_void_p())
    c_usr_conf_dir = _encode_str(usr_conf_dir)
    c_etc_conf_dir = _encode_str(etc_conf_dir)
    c_project_name = _encode_str(project_name)
    c_config_suffix = _encode_str(config_suffix)
    err = libeconf.econf_readDirs(
        byref(result.ptr),
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
) -> list[Keyfile]:
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
    :return: list of Keyfile objects
    """
    key_files = c_void_p(None)
    c_size = c_size_t()
    c_usr_conf_dir = _encode_str(usr_conf_dir)
    c_etc_conf_dir = _encode_str(etc_conf_dir)
    c_project_name = _encode_str(project_name)
    c_config_suffix = _encode_str(config_suffix)
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
    if err:
        raise _exceptions(
            err, f"read_dirs_history failed with error: {err_string(err)}"
        )
    arr = cast(key_files, POINTER(c_void_p * c_size.value))
    result = [Keyfile(c_void_p(i)) for i in arr.contents]
    return result


def new_key_file(delim: str | bytes, comment: str | bytes) -> Keyfile:
    """
    Create a new empty keyfile

    :param delim: delimiter of a key/value e.g. '='
    :param comment: string that defines the start of a comment e.g. '#'
    :return: created Keyfile object
    """
    result = Keyfile(c_void_p)
    delim = _encode_str(delim)
    comment = _encode_str(comment)
    err = libeconf.econf_newKeyFile(byref(result.ptr), delim, comment)
    if err:
        raise _exceptions(err, f"new_key_file failed with error: {err_string(err)}")
    return result


def new_ini_file() -> Keyfile:
    """
    Create a new empty keyfile with delimiter '=' and comment '#'

    :return: created Keyfile object
    """
    result = Keyfile(c_void_p)
    err = libeconf.econf_newIniFile(byref(result.ptr))
    if err:
        raise _exceptions(err, f"new_ini_file failed with error: {err_string(err)}")
    return result


def write_file(kf: Keyfile, save_to_dir: str, file_name: str) -> Econf_err:
    """
    Write content of a keyfile to specified location

    :param kf: Key-Value storage object
    :param save_to_dir: directory into which the file has to be written
    :param file_name: filename with suffix of the to be written file
    :return: Error code
    """
    c_save_to_dir = _encode_str(save_to_dir)
    c_file_name = _encode_str(file_name)
    err = libeconf.econf_writeFile(byref(kf.ptr), c_save_to_dir, c_file_name)
    return Econf_err(err)


def get_path(kf: Keyfile) -> str:
    """
    Get the path of the source of the given key file

    :param kf: Key-Value storage object
    :return: path of the config file as string
    """
    # extract from pointer
    libeconf.econf_getPath.restype = c_char_p
    return libeconf.econf_getPath(kf.ptr).decode("utf-8")


def get_groups(kf: Keyfile) -> list[str]:
    """
    List all the groups of given keyfile

    :param kf: Key-Value storage object
    :return: list of groups in the keyfile
    """
    c_length = c_size_t()
    c_groups = c_void_p(None)
    err = libeconf.econf_getGroups(kf.ptr, byref(c_length), byref(c_groups))
    if err:
        _exceptions(err, f"get_groups failed with error: {err_string(err)}")
    arr = cast(c_groups, POINTER(c_char_p * c_length.value))
    result = [i.decode("utf-8") for i in arr.contents]
    return result


# Not passing a group currently leads to ECONF_NOKEY error
def get_keys(kf: Keyfile, group: str) -> list[str]:
    """
    List all the keys of a given group or all keys in a keyfile

    :param kf: Key-Value storage object
    :param group: group of the keys to be returned
    :return: list of keys in the given group
    """
    c_length = c_size_t()
    c_keys = c_void_p(None)
    group = _encode_str(group)
    err = libeconf.econf_getKeys(kf.ptr, group, byref(c_length), byref(c_keys))
    if err:
        _exceptions(err, f"get_keys failed with error: {err_string(err)}")
    arr = cast(c_keys, POINTER(c_char_p * c_length.value))
    result = [i.decode("utf-8") for i in arr.contents]
    return result


def get_int_value(kf: Keyfile, group: str, key: str) -> int:
    """
    Return an integer value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_int64()
    err = libeconf.econf_getInt64Value(kf.ptr, c_group, c_key, byref(c_result))
    if err:
        _exceptions(err, f"get_int64_value failed with error: {err_string(err)}")
    return c_result.value


def get_uint_value(kf: Keyfile, group: str, key: str) -> int:
    """
    Return an unsigned integer value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_uint64()
    err = libeconf.econf_getUInt64Value(kf.ptr, c_group, c_key, byref(c_result))
    if err:
        _exceptions(err, f"get_uint64_value failed with error: {err_string(err)}")
    return c_result.value


def get_float_value(kf: Keyfile, group: str, key: str) -> float:
    """
    Return a float value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_double()
    err = libeconf.econf_getDoubleValue(kf.ptr, c_group, c_key, byref(c_result))
    if err:
        _exceptions(err, f"get_double_value failed with error: {err_string(err)}")
    return c_result.value


def get_string_value(kf: Keyfile, group: str, key: str) -> str:
    """
    Return a string value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_char_p()
    err = libeconf.econf_getStringValue(kf.ptr, c_group, c_key, byref(c_result))
    if err:
        _exceptions(err, f"get_string_value failed with error: {err_string(err)}")
    return c_result.value.decode("utf-8")


def get_bool_value(kf: Keyfile, group: str, key: str) -> bool:
    """
    Return a boolean value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_bool()
    err = libeconf.econf_getBoolValue(kf.ptr, c_group, c_key, byref(c_result))
    if err:
        _exceptions(err, f"get_bool_value failed with error: {err_string(err)}")
    return c_result.value


def get_int_value_def(kf: Keyfile, group: str, key: str, default: int) -> int:
    """
    Return an integer value for given group/key or return a default value if key is not found

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_int64()
    if not isinstance(default, int):
        raise TypeError(f"\"default\" parameter must be of type int")
    if not _check_int_overflow(default):
        raise ValueError(f"Integer overflow found, only up to 64 bit integers are supported")
    c_default = c_int64(default)
    err = libeconf.econf_getInt64ValueDef(
        kf.ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_int64_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_uint_value_def(kf: Keyfile, group: str, key: str, default: int) -> int:
    """
    Return an unsigned integer value for given group/key or return a default value if key is not found

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_uint64()
    if not isinstance(default, int) | (default < 0):
        raise TypeError(f"\"default\" parameter must be of type int and greater or equal to zero")
    if not _check_uint_overflow(default):
        raise ValueError(f"Integer overflow found, only up to 64 bit unsigned integers are supported")
    c_default = c_uint64(default)
    err = libeconf.econf_getUInt64ValueDef(
        kf.ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_uint64_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_float_value_def(kf: Keyfile, group: str, key: str, default: float) -> float:
    """
    Return a float value for given group/key or return a default value if key is not found

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_double()
    if not isinstance(default, float):
        raise TypeError(f"\"default\" parameter must be of type float")
    if not _check_float_overflow(default):
        raise ValueError(f"Float overflow found, only up to 64 bit floats are supported")
    c_default = c_double(default)
    err = libeconf.econf_getDoubleValueDef(
        kf.ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_double_value_def failed with error: {err_string(err)}")
    return c_result.value


def get_string_value_def(kf: Keyfile, group: str, key: str, default: str) -> str:
    """
    Return a string value for given group/key or return a default value if key is not found

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_char_p()
    c_default = _encode_str(default)
    err = libeconf.econf_getStringValueDef(
        kf.ptr, c_group, c_key, byref(c_result), c_default
    )
    if err:
        if err == 5:
            return c_default.decode("utf-8")
        _exceptions(err, f"get_string_value_def failed with error: {err_string(err)}")
    return c_result.value.decode("utf-8")


def get_bool_value_def(kf: Keyfile, group: str, key: str, default: bool) -> bool:
    """
    Return a boolean value for given group/key or return a default value if key is not found

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param default: value to be returned if no key is found
    :return: value of the key
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_result = c_bool()
    if not isinstance(default, bool):
        raise TypeError(f"\"value\" parameter must be of type bool")
    c_default = c_bool(default)
    err = libeconf.econf_getBoolValueDef(kf.ptr, c_group, c_key, byref(c_result), c_default)
    if err:
        if err == 5:
            return c_default.value
        _exceptions(err, f"get_bool_value_def failed with error: {err_string(err)}")
    return c_result.value


def set_int_value(kf: Keyfile, group: str, key: str, value: int) -> Econf_err:
    """
    Setting an integer value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, int):
        raise TypeError(f"\"value\" parameter must be of type int")
    if not _check_int_overflow(value):
        raise ValueError(f"Integer overflow found, only up to 64 bit integers are supported")
    c_value = c_int64(value)
    err = libeconf.econf_setInt64Value(byref(kf.ptr), c_group, c_key, c_value)
    if err:
        _exceptions(err, f"set_int64_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_uint_value(kf: Keyfile, group: str, key: str, value: int) -> Econf_err:
    """
    Setting an unsigned integer value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, int) | (value < 0):
        raise TypeError(f"\"value\" parameter must be of type int and be greater or equal to zero")
    if not _check_uint_overflow(value):
        raise ValueError(f"Integer overflow found, only up to 64 bit unsigned integers are supported")
    c_value = c_uint64(value)
    err = libeconf.econf_setUInt64Value(byref(kf.ptr), c_group, c_key, c_value)
    if err:
        _exceptions(err, f"set_uint64_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_float_value(kf: Keyfile, group: str, key: str, value: float) -> Econf_err:
    """
    Setting a float value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, float):
        raise TypeError(f"\"value\" parameter must be of type float")
    if not _check_float_overflow(value):
        raise ValueError(f"Float overflow found, only up to 64 bit floats are supported")
    c_value = c_double(value)
    err = libeconf.econf_setDoubleValue(byref(kf.ptr), c_group, c_key, c_value)
    if err:
        _exceptions(err, f"set_double_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_string_value(kf: Keyfile, group: str, key: str, value: str | bytes) -> Econf_err:
    """
    Setting a string value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    c_value = _encode_str(value)
    err = libeconf.econf_setStringValue(byref(kf.ptr), c_group, c_key, c_value)
    if err:
        _exceptions(err, f"set_string_value failed with error: {err_string(err)}")
    return Econf_err(err)


def set_bool_value(kf: Keyfile, group: str, key: str, value: bool) -> Econf_err:
    """
    Setting a boolean value for given group/key

    :param kf: Key-Value storage object
    :param group: desired group
    :param key: key of the value that is requested
    :param value: value to be set for given key
    :return: Error code
    """
    c_group = _encode_str(group)
    c_key = _encode_str(key)
    if not isinstance(value, bool):
        raise TypeError(f"\"value\" parameter must be of type bool")
    c_value = c_bool(value)
    err = libeconf.econf_setBoolValue(byref(kf.ptr), c_group, c_key, c_value)
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
    libeconf.econf_errString.restype = c_char_p
    return libeconf.econf_errString(error).decode("utf-8")


def err_location():
    """
    Info about the line where an error happened

    :return: path to the last handled file and number of last handled line
    """
    c_filename = c_char_p()
    c_line_nr = c_uint64()
    libeconf.econf_errLocation(byref(c_filename), byref(c_line_nr))
    return c_filename.value, c_line_nr.value


def free_file(kf: Keyfile):
    """
    Free the memory of a given keyfile

    :param kf: Keyfile to be freed
    :return: None
    """
    libeconf.econf_freeFile(kf.ptr)
    return
