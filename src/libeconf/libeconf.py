import ctypes.util
from enum import Enum
import pathlib
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


class file_entry(Structure):
    _fields_ = [
        ("group", c_char_p),
        ("key", c_char_p),
        ("value", c_char_p),
        ("comment_before_key", c_char_p),
        ("comment_after_value", c_char_p),
        ("line_number", c_uint64),
        ("quotes", c_bool)
    ]


class econf_file(Structure):
    _fields_ = [
        ("file_entry", file_entry),
        ("length", c_size_t),
        ("alloc_length", c_size_t),
        ("delimiter", c_char),
        ("comment", c_char),
        ("on_merge_delete", c_bool),
        ("path", c_char_p)
    ]


libname = ctypes.util.find_library("econf")
econf = CDLL(libname)


def econf_set_Value():
    pass


def econf_free():
    pass


def econf_readFile(file_name: bytes, delim: bytes, comment: bytes):
    # return Pointer to object, no need to parse it
    result = c_void_p(None)
    err = econf.econf_readFile(byref(result), file_name, delim, comment)
    if err != 0:
        print("readFile: ", Econf_err(err))
        return Econf_err(err)
    # print(hex(result.value))
    return result


def econf_mergeFiles():
    pass


def econf_readDirs():
    pass


def econf_readDirsHistory():
    pass


def econf_newkeyFile():
    pass


def econf_newIniFile():
    pass


def econf_writeFile(kf, save_to_dir, file_name):
    c_save_to_dir = c_char_p(save_to_dir)
    c_file_name = c_char_p(file_name)
    err = econf.econf_writeFile(byref(kf), c_save_to_dir, c_file_name)
    return err


def econf_getPath(kf):
    # extract from pointer
    return econf.econf_getPath(kf)


def econf_getGroups(kf):
    c_length = c_size_t()
    c_groups = c_void_p(None)
    err = econf.econf_getGroups(kf, byref(c_length), byref(c_groups))
    if err != 0:
        print("getGroups: ", Econf_err(err))
        return Econf_err(err)
    arr = cast(c_groups, POINTER(c_char_p * c_length.value))
    result = [i for i in arr.contents]
    return result


# Not passing a group currently leads to ECONF_NOKEY error
def econf_getKeys(kf, group=None):
    c_length = c_size_t()
    c_keys = c_void_p(None)
    err = econf.econf_getKeys(kf, group, byref(c_length), byref(c_keys))
    if err != 0:
        print("getKeys: ", Econf_err(err))
        return Econf_err(err)
    arr = cast(c_keys, POINTER(c_char_p * c_length.value))
    result = [i for i in arr.contents]
    return result


def econf_getIntValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int32()
    err = econf.econf_getIntValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getIntValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getInt64Value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int64()
    err = econf.econf_getInt64Value(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getInt64Value: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getUIntValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint32()
    err = econf.econf_getUIntValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getUIntValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getUInt64Value(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint64()
    err = econf.econf_getUInt64Value(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getUInt64Value: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getFloatValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_float()
    err = econf.econf_getFloatValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getFloatValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getDoubleValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_double()
    err = econf.econf_getDoubleValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getDoubleValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getStringValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_char_p()
    err = econf.econf_getStringValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getStringValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getBoolValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_bool()
    err = econf.econf_getBoolValue(kf, c_group, c_key, byref(c_result))
    if err != 0:
        print("getBoolValue: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getIntValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int32()
    c_default = c_int32(default)
    err = econf.econf_getIntValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getIntValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getInt64ValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_int64()
    c_default = c_int64(default)
    err = econf.econf_getInt64ValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getInt64ValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getUIntValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint32()
    c_default = c_uint32(default)
    err = econf.econf_getUIntValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getUIntValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getUInt64ValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_uint64()
    c_default = c_uint64(default)
    err = econf.econf_getUInt64ValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getUInt64ValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getFloatValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_float()
    c_default = c_float(default)
    err = econf.econf_getFloatValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getFloatValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getDoubleValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_double()
    c_default = c_double(default)
    err = econf.econf_getDoubleValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getDoubleValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getStringValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_char_p()
    c_default = c_char_p(default)
    err = econf.econf_getStringValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getStringValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_getBoolValueDef(kf, group, key, default):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_result = c_bool()
    c_default = c_bool(default)
    err = econf.econf_getBoolValueDef(kf, c_group, c_key, byref(c_result), c_default)
    if err != 0:
        if err == 5:
            return c_default.value
        print("getBoolValueDef: ", Econf_err(err))
        return Econf_err(err)
    return c_result.value


def econf_setIntValue():
    pass


def econf_setInt64Value():
    pass


def econf_setInt64value():
    pass


def econf_setUIntValue():
    pass


def econf_setUInt64Value():
    pass


def econf_setFloatValue():
    pass


def econf_setDoubleValue():
    pass


def econf_setStringValue():
    pass


def econf_setBoolValue():
    pass


def econf_errString():
    pass


def econf_freeArray():
    pass


def econf_freeFile():
    pass
