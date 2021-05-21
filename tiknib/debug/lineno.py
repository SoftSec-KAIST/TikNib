import os
import re
import pickle

from elftools.elf.elffile import ELFFile


# Slightly modified below code:
# https://github.com/eliben/pyelftools/blob/master/examples/dwarf_decode_address.py
def decode_file_line(dwarfinfo, func_addrs):
    # Go over all the line programs in the DWARF information.
    ret = {}
    for CU in dwarfinfo.iter_CUs():
        # Look at line programs to find the file/line for the address
        lineprog = dwarfinfo.line_program_for_CU(CU)
        for entry in lineprog.get_entries():
            if entry.state is None:
                continue
            if entry.state.end_sequence:
                continue
            # We check if an address is in the given set of function addresses.
            cur_state = entry.state
            if cur_state.address not in func_addrs:
                continue

            file_name = b""
            try:
                file_name = lineprog["file_entry"][cur_state.file - 1].name
                # To obtain full path
                dir_name = CU.get_top_DIE().attributes["DW_AT_comp_dir"].value
                path_name = CU.get_top_DIE().attributes["DW_AT_name"].value
                file_name = os.path.join(dir_name, path_name)
            except:
                pass

            if isinstance(file_name, bytes):
                file_name = file_name.decode()

            line = cur_state.line
            ret[cur_state.address] = (file_name, line)

    return ret


def fetch_lineno(bin_name, func_addrs):
    addr_to_line = {}
    with open(bin_name, "rb") as f:
        elffile = ELFFile(f)
        if not elffile.has_dwarf_info():
            print("No Dwarf Found in ", bin_name)
        else:
            dwarf = elffile.get_dwarf_info()
            addr_to_line = decode_file_line(dwarf, func_addrs)

    return addr_to_line
