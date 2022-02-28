import os
import sys
import time
from optparse import OptionParser

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.debug.lineno import fetch_lineno
from tiknib.utils import do_multiprocess
from tiknib.utils import load_func_data, store_func_data
from tiknib.utils import parse_source_path
from config.path_variables import IDA_PATH, IDA_FETCH_FUNCDATA

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO)

def extract_func_lineno(bin_name):
    try:
        bin_name, func_data_list = load_func_data(bin_name)
    except:
        print(bin_name)
        return bin_name

    func_addrs = dict(map(lambda x: (x["startEA"], x["name"]), func_data_list))
    line_map = fetch_lineno(bin_name, func_addrs)
    for func in func_data_list:
        func_addr = func["startEA"]
        if func_addr not in line_map or not line_map[func_addr][0]:
            continue
        func["src_path"] = line_map[func_addr][0]
        func["src_file"] = parse_source_path(func["src_path"])
        func["src_line"] = line_map[func_addr][1]
        # Fix ase18 source paths coreutils-6.7-6.5 / coreutils-6.7-6.7
        if 'coreutils-6.7-6.5' in func['src_path']:
            func['src_path'] = func['src_path'].replace('6.7-6.5', '6.5')
    store_func_data(bin_name, func_data_list)
    return

if __name__ == "__main__":
    op = OptionParser()
    op.add_option(
        "--input_list",
        type="str",
        action="store",
        dest="input_list",
        help="a file containing a list of input binaries",
    )
    op.add_option(
        "--threshold",
        type="int",
        action="store",
        dest="threshold",
        default=1,
        help="number of binaries to process in parallel",
    )
    op.add_option(
        "--chunk_size",
        type="int",
        action="store",
        dest="chunk_size",
        default=1,
        help="number of binaries to process in each process",
    )
    op.add_option("--force", action="store_true", dest="force")
    (opts, args) = op.parse_args()

    assert opts.input_list

    with open(opts.input_list, "r") as f:
        bins = f.read().splitlines()

    t0 = time.time()
    logger.info("Processing %d binaries ...", len(bins))
    failed_bins = do_multiprocess(
        extract_func_lineno, bins, chunk_size=opts.chunk_size, threshold=opts.threshold
    )
    logger.info("done. (%0.3fs)", (time.time() - t0))

    failed_bins = list(filter(lambda x: x is not None, failed_bins))
    if failed_bins:
        print("{} bins failed.".format(len(failed_bins)))

        with open("failed_bins.txt", "w") as f:
            for b in failed_bins:
                f.write(b + "\n")

        from tiknib.idascript import IDAScript
        idascript = IDAScript(
            idapath=IDA_PATH,
            idc=IDA_FETCH_FUNCDATA,
            force=True,
            log=True,
        )
        idascript.run("failed_bins.txt")

        logger.info("Re-Processing %d binaries ...", len(failed_bins))
        do_multiprocess(
            extract_func_lineno, failed_bins, chunk_size=opts.chunk_size, threshold=opts.threshold
        )
        logger.info("done. (%0.3fs)", (time.time() - t0))
