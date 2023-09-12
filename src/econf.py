import ctypes.util
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


libname = ctypes.util.find_library("econf")
libeconf = CDLL(libname)


def setValue(kf, group, key, value):
    if isinstance(value, int):
        res = set_int_value(kf, group, key, value)
    # elif isinstance(value, long):
    #     res = econf_setInt64Value(kf, group, key, value)
    # elif isinstance(value, uint):
    #     res = econf_setUIntValue(kf, group, key, value)
    # elif isinstance(value, ulong):
    #     res = econf_setUInt64Value(kf, group, key, value)
    elif isinstance(value, float):
        res = set_float_value(kf, group, key, value)
    # elif isinstance(value, double):
    #     res = econf_setDoubleValue(kf, group, key, value
    elif isinstance(value, str):
        res = set_string_value(kf, group, key, value)
    elif isinstance(value, bool):
        res = set_bool_value(kf, group, key, value)
    return res


def read_file(file_name: bytes, delim: bytes, comment: bytes):
    # return Pointer to object, no need to parse it
    result = c_void_p(None)
    err = libeconf.econf_readFile(byref(result), file_name, delim, comment)
    if err != 0:
        print("readFile: ", Econf_err(err))
        return Econf_err(err)
    return result


def merge_files(usr_file, etc_file):
    merged_file = c_void_p(None)
    err = libeconf.econf_mergeFiles(byref(merged_file), usr_file, etc_file)
    if err != 0:
        print("mergeFiles: ", Econf_err(err))
        return Econf_err(err)
    return merged_file


# this reads either the first OR the second file if the first one does not exist
def read_dirs(usr_conf_dir, etc_conf_dir, project_name, config_suffix, delim, comment):
    result = c_void_p(None)
    c_usr_conf_dir = c_char_p(usr_conf_dir)
    c_etc_conf_dir = c_char_p(etc_conf_dir)
    c_project_name = c_char_p(project_name)
    c_config_suffix = c_char_p(config_suffix)
    err = libeconf.econf_readDirs(byref(result), c_usr_conf_dir, c_etc_conf_dir, c_project_name, c_config_suffix, delim, comment)
    if err != 0:
        print("readDirs: ", Econf_err(err))
        return Econf_err(err)
    return result


# this reads either the first OR the second file if the first one does not exist
def read_dirs_history(usr_conf_dir, etc_conf_dir, project_name, config_suffix, delim, comment):
    key_files = c_void_p(None)
    c_size = c_size_t()
    c_usr_conf_dir = c_char_p(usr_conf_dir)
    c_etc_conf_dir = c_char_p(etc_conf_dir)
    c_project_name = c_char_p(project_name)
    c_config_suffix = c_char_p(config_suffix)
    err = libeconf.econf_readDirsHistory(byref(key_files), byref(c_size), c_usr_conf_dir, c_etc_conf_dir, c_project_name, c_config_suffix, delim, comment)
    if err != 0:
        print("readDirsHistory: ", Econf_err(err))
        return Econf_err(err)
    arr = cast(key_files, POINTER(c_void_p * c_size.value))
    result = [c_void_p(i) for i in arr.contents]
    return result


def new_key_file(delim, comment):
    result = c_void_p(None)
    c_delim = c_char(delim)
    c_comment = c_char(comment)
    err = libeconf.econf_newKeyFile(result, c_delim, c_comment)
    if err != 0:
        print("newKeyFile: ", Econf_err(err))
        return Econf_err(err)
    return result


def new_ini_file():
    result = c_void_p(None)
    err = libeconf.econf_newIniFile(result)
    if err != 0:
        print("newIniFile: ", Econf_err(err))
        return Econf_err(err)
    return result


def write_file(kf, save_to_dir, file_name):
    c_save_to_dir = c_char_p(save_to_dir)
    c_file_name = c_char_p(file_name)
    err = libeconf.econf_writeFile(byref(kf), c_save_to_dir, c_file_name)
    return err


def get_path(kf):
    # extract from pointer
    libeconf.econf_getPath.restype = c_char_p
    return libeconf.econf_getPath(kf)


def get_groups(kf):
    c_length = c_size_t()
    c_groups = c_void_p(None)
    err = libeconf.econf_getGroups(kf, byref(c_length), byref(c_groups))
    if err != 0:
        print("getGroups: ", Econf_err(err))
        return Econf_err(err)
    arr = cast(c_groups, POINTER(c_char_p * c_length.value))
    result = [i for i in arr.contents]
    return result


# Not passing a group currently leads to ECONF_NOKEY error
def get_keys(kf, group=None):
    c_length = c_size_t()
    c_keys = c_void_p(None)
    err = libeconf.econf_getKeys(kf, group, byref(c_length), byref(c_keys))
    if err != 0:
        print("getKeys: ", Econf_err(err))
        return Econf_err(err)
    arr = cast(c_keys, POINTER(c_char_p * c_length.value))
    result = [i for i in arr.contents]
    return result


def get_int_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int32()
    err = libeconf.econf_getIntValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getIntValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_int64_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int64()
    err = libeconf.econf_getInt64Value(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getInt64Value: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_uint_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint32()
    err = libeconf.econf_getUIntValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getUIntValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_uint64_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint64()
    err = libeconf.econf_getUInt64Value(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getUInt64Value: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_float_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_float()
    err = libeconf.econf_getFloatValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getFloatValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_double_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_double()
    err = libeconf.econf_getDoubleValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getDoubleValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_string_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_char_p()
    err = libeconf.econf_getStringValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getStringValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_bool_value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_bool()
    err = libeconf.econf_getBoolValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getBoolValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_int_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int32()
    c_default = c_int32(default)
    err = libeconf.econf_getIntValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getIntValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_int64_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int64()
    c_default = c_int64(default)
    err = libeconf.econf_getInt64ValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getInt64ValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_uint_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint32()
    c_default = c_uint32(default)
    err = libeconf.econf_getUIntValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getUIntValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_uint64_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint64()
    c_default = c_uint64(default)
    err = libeconf.econf_getUInt64ValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getUInt64ValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_float_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_float()
    c_default = c_float(default)
    err = libeconf.econf_getFloatValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getFloatValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_double_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_double()
    c_default = c_double(default)
    err = libeconf.econf_getDoubleValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getDoubleValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_string_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_char_p()
    c_default = c_char_p(default)
    err = libeconf.econf_getStringValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getStringValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def get_bool_value_def(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_bool()
    c_default = c_bool(default)
    err = libeconf.econf_getBoolValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getBoolValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def set_int_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_int32(value)
    err = libeconf.econf_setIntValue(kf, c_group, c_key, c_value)
    if err != 0:
        print("setIntvalue: ", Econf_err(err))
    return Econf_err(err)


def set_int64_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_int64(value)
    err = libeconf.econf_setInt64Value(kf, c_group, c_key, c_value)
    if err != 0:
        print("setInt64value: ", Econf_err(err))
    return Econf_err(err)


def set_uint_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_uint32(value)
    err = libeconf.econf_setUIntValue(kf, c_group, c_key, c_value)
    if err != 0:
        print("setUIntvalue: ", Econf_err(err))
    return Econf_err(err)


def set_uint64_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_uint64(value)
    err = libeconf.econf_setUInt64Value(kf, c_group, c_key, c_value)
    if err != 0:
        print("setUInt64value: ", Econf_err(err))
    return Econf_err(err)


def set_float_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_float(value)
    err = libeconf.econf_setFloatValue(kf, c_group, c_key, c_value)
    if err != 0:
        print("setFloatvalue: ", Econf_err(err))
    return Econf_err(err)


def set_double_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_double(value)
    err = libeconf.econf_setDoubleValue(kf, c_group, c_key, c_value)
    if err != 0:
        print("setDoublevalue: ", Econf_err(err))
    return Econf_err(err)


def set_string_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_char_p(value)
    err = libeconf.econf_setStringValue(kf, c_group, c_key, c_value)
    if err != 0:
        print("setStringvalue: ", Econf_err(err))
    return Econf_err(err)


def set_bool_value(kf, group, key, value):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_value = c_bool(value)
    err = libeconf.econf_setBoolValue(kf, c_group, c_key, c_value)
    if err != 0:
        print("setBoolvalue: ", Econf_err(err))
    return Econf_err(err)


def err_string(error):
    c_int(error)
    libeconf.econf_errString.restype = c_char_p
    return libeconf.econf_errString(error)


def err_location(filename, line_nr):
    c_filename = c_char_p(filename)
    c_line_nr = c_uint64(line_nr)
    libeconf.econf_errLocation(byref(c_filename), byref(c_line_nr))
    return c_filename.value, c_line_nr.value


def free_file(kf):
    libeconf.econf_freeFile(kf)
    return
