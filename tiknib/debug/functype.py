import os
import re
import ctags
from ctags import CTags, TagEntry

from tiknib.utils import system, do_multiprocess

import logging

logger = logging.getLogger(__name__)

# preset of known types
CHAR_TYPES = [
    "byte",
    "char",
    "uchar",
    "__int8",
    "uint8_t",
]

SHORT_TYPES = [
    "wchar_t",
    "uint16_t",
    "__int16",
]

INT_TYPES = [
    "int",
    "ssize_t",
    "off_t",
    "arith_t",
    "arith_t_0",
    "number_t",
    "int32_t",
    "bb_wint_t",
    "wint_t",
    "COST",
    # this can be long
    "intmax_t",
    # unsigned
    "size_t",
    "time_t",
    "leasetime_t",
    "cputime_t",
    "uoff_t",
    "speed_t",
    "pid_t",
    "uintptr_t",
    "uintmax_t",
    "unsigned int",
    "AEP_U32",
    "AEP_RV",
    "AEP_CONNECTION_HNDL",
    "sector_t",
    "mode_t",
    "__mode_t",
    "operand_0",
    "ulg",
    "uid_t",
    "gid_t",
    "dev_t",
    "socklen_t",
    "count",
    "nfds_t",
    "token_t",
    "data_t",
    "ino_t",
    "word32",
    "IPos",
    "SW_U32",
    "SW_CONTEXT_HANDLE",
    "ptrdiff_t",
    "xtime_t",
    "cc_t",
    "randint",
    "__re_idx_t",
    "__re_size_t",
    "Idx",
    "reg_syntax_t",
    "re_token_t",
    "re_hashval_t",
    "regoff_t",
    "uint32_t",
    # 64 bit
    "ullong",
    "__int64",
    "uint64_t",
    "__uint64_t",
    "int64_t",
    "BFD_HOST_U_64_BIT",
]

FLOAT_TYPES = [
    "double",
    "long double",
    "float",
]

STRUCT_TYPES = [
    "complex_float",
    "stack_st_X509",
    "FILE",
]

PRIMITIVE_TYPES = {
    "bool": "char",
    "void": "void",
    "char": "char",
    "short": "short",
    "int": "int",
    "int64": "int64",
    "float": "float",
    "enum": "enum",
    "struct": "struct",
    "func": "func",
    "union": "union",
}


def get_default_type_map():
    return PRIMITIVE_TYPES.copy()


def update_known_types(type_map):
    for x in INT_TYPES:
        type_map[x] = "int"
    for x in CHAR_TYPES:
        type_map[x] = "char"
    for x in SHORT_TYPES:
        type_map[x] = "short"
    for x in FLOAT_TYPES:
        type_map[x] = "float"
    for x in STRUCT_TYPES:
        type_map[x] = "struct"


def sanitize(ret_type):
    if ret_type is None:
        return "void"

    orig = ret_type
    ret_type = re.sub("_\d*$", "", ret_type)
    ret_type = re.sub("(typedef|static|const|unsigned|signed)", "", ret_type)
    ret_type = re.sub("\/\^ *", "", ret_type)
    ret_type = ret_type.strip()
    if not ret_type:
        ret_type = "int"

    return ret_type


def update_type_map(type_map, ctags_fname):
    logger.debug("processing %s ...", ctags_fname)
    tag = CTags(ctags_fname.encode())
    tag.setSortType(ctags.TAG_SORTED)
    entry = TagEntry()

    # First traverse all entries
    status = tag.first(entry)
    while status:
        name = entry["name"].decode()
        kind = entry["kind"].decode()
        typeref = (entry[b"typeref"] or b"").decode()
        pattern = entry["pattern"].decode()

        # TODO: Check multiple declaration
        if name in type_map:
            status = tag.next(entry)
            continue

        # TODO: handle macro properly. currently, assume macros are integers.
        # Also, skip allocation.
        if kind == "macro" or "=" in pattern:
            status = tag.next(entry)
            continue

        if kind in ["func", "proc", "function", "procedure", "method"]:
            ret_type = "func"
        elif kind.startswith("enum"):
            ret_type = "enum"
        elif kind == "union":
            ret_type = "union"
        elif kind.startswith("struct"):
            ret_type = "struct"
        elif kind.startswith("class"):
            ret_type = "struct"
        elif kind == "label":
            ret_type = ret_type
        elif kind in ["label", "typedef", "member", "variable"]:
            if typeref:
                ret_type = typeref.split(":")[0]
            else:
                ret_type = pattern[: pattern.rindex(name)].rstrip()
        else:
            status = tag.next(entry)
            continue

        ret_type = sanitize(ret_type)

        if "(" in ret_type:
            ret_type = "func"

        if "*" in ret_type:
            ret_type + " *"

        type_map[name] = ret_type
        status = tag.next(entry)

    # Now check until no update exists
    while True:
        is_updated = False
        status = tag.first(entry)
        while status:
            name = entry["name"].decode()
            kind = entry["kind"].decode()
            typeref = (entry[b"typeref"] or b"").decode()
            pattern = entry["pattern"].decode()

            # No need to handle a macro as it is already replaced by a constant.
            # Also, skip allocation.
            if kind == "macro" or "=" in pattern:
                status = tag.next(entry)
                continue

            if name not in type_map:
                ret_type = "int"
            else:
                ret_type = type_map[name]
                ret_type = ret_type.split()[0]  # remove pointer for here
                while ret_type in type_map and ret_type != type_map[ret_type]:
                    ret_type = ret_type.split()[0]  # remove pointer for here
                    ret_type = type_map[ret_type]

                if ret_type not in type_map:
                    ret_type = "int"

                # use a single '*' for denoting a pointer
                if "*" not in ret_type and "*" in type_map[name]:
                    ret_type = ret_type + " *"

                if ret_type != type_map[name]:
                    type_map[name] = ret_type
                    is_updated = True

            status = tag.next(entry)

        if is_updated == False:
            break

    return None


def create_ctags(source_list, ctags_dir):
    with open(source_list, "r") as f:
        lines = f.read().splitlines()

    for dir_name in lines:
        basename = os.path.basename(dir_name.strip())
        if os.path.exists(os.path.join(ctags_dir, basename + ".tags")):
            continue

        cmd = 'ctags -f "{0}/{1}.tags" --fields=afmikKlnsStz -R "{2}"'
        cmd = cmd.format(ctags_dir, basename, dir_name)
        system(cmd)

    if not os.path.exists(os.path.join(ctags_dir, "include.tags")):
        cmd = 'ctags -f "{0}/include.tags" --fields=afmikKlnsStz -R "{1}"'
        cmd = cmd.format(ctags_dir, "/usr/include/")
        system(cmd)


def fetch_type(type_map, t):
    t = sanitize(t)
    ret = t.split()[0]
    if ret in type_map:
        ret = type_map[ret]
    else:
        ret = "int"

    if "*" not in ret and "*" in t:
        ret = ret + " *"

    return ret
