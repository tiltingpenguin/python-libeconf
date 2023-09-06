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
libeconf = CDLL(libname)


def econf_set_Value():
    pass


def econf_free():
    pass


def econf_readFile(file_name, delim, comment):
    # return Pointer to object, no need to parse it
    result = c_void_p(None)
    c_file_name = file_name
    c_delim = c_char(delim)
    c_comment = c_char(comment)
    err = libeconf.econf_readFile(byref(result), c_file_name, byref(c_delim), byref(c_comment))
    if err != 0:
        print(Econf_err(err))
    return byref(result)


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


def econf_writeFile():
    pass


def econf_getPath():
    pass


def econf_getGroups():
    pass


def econf_geKeys():
    pass


def econf_getIntValue(kf, group, key):
    c_group = c_char_p(group)
    c_key = c_char_p(key)
    c_res = c_int32()
    err = libeconf.econf_getIntValue(kf, byref(c_group), byref(c_key), byref(c_res))
    if err != 0:
        print(Econf_err(err))
    return c_res.value


def econf_getInt64Value():
    pass


def econf_getUIntValue():
    pass


def econf_getUInt64Value():
    pass


def econf_getFloatValue():
    pass


def econf_getDoubleValue():
    pass


def econf_getStringValue():
    pass


def econf_getBoolValue():
    pass


def econf_getIntValueDef():
    pass


def econf_getInt64ValueDef():
    pass


def econf_getUIntValueDef():
    pass


def econf_getUInt64ValueDef():
    pass


def econf_getFloatValueDef():
    pass


def econf_getDoubleVallueDef():
    pass


def econf_getStringValueDef():
    pass


def econf_getBoolValueDef():
    pass


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
