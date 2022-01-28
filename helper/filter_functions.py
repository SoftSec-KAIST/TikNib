import os
import sys
import time
from optparse import OptionParser

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.utils import do_multiprocess
from tiknib.utils import load_func_data, store_func_data
from tiknib.utils import parse_fname
from tiknib.utils import parse_source_path
from tiknib.utils import system

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO)



g_oracle = None
def filter_funcs(bin_path):
    global g_oracle
    bin_path, func_data_list = load_func_data(bin_path)
    func_data_list = sorted(func_data_list, key=lambda x: x['name'])
    num_orig_funcs = len(func_data_list)
    pack_name = func_data_list[0]['package']

    # filter functions by segment name (consider functions in code segment)
    funcs = list(filter(lambda x: x['seg_name'] == '.text', func_data_list))
    num_code_funcs = len(funcs)

    funcs = list(filter(lambda x: 'src_path' in x and x['src_path'], funcs))
    num_src_funcs = len(funcs)

    # To identify functions inserted by compilers
    #for func in funcs:
    #    if func['package'] not in func['src_file']:
    #        print(func['name'], func['src_file'], func['src_line'])

    # filter functions by package name (remove functions inserted by compilers)
    funcs = list(filter(lambda x: pack_name in x['src_path'], funcs))
    num_pack_funcs = len(funcs)

    if num_pack_funcs == 0:
        print("No functions: ", pack_name, bin_path, num_orig_funcs)

    funcs = list(filter(lambda x: not x['name'].startswith('sub_'), funcs))
    num_sub_funcs = len(funcs)

    names = set(map(lambda x: x['name'], funcs))
    sources = set(map(lambda x: (x['src_file'], x['src_line']), funcs))

    if g_oracle:
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        funcs = list(filter(
            lambda x:
            x['src_file'] in g_oracle[pack_name][bin_name]
            and x['src_line'] in g_oracle[pack_name][bin_name][x['src_file']],
            funcs))
        # TODO: handle suffix correctly.
        store_func_data(bin_path, funcs, suffix="filtered")
    num_oracle_funcs = len(funcs)
    num_readelf_funcs = 0
#    if g_oracle:
#        cmd = "readelf -s {} | grep FUNC | grep -v UND | wc -l".format(bin_path)
#        cmd = " objdump --syms -j .text {} | grep \"F .text\" | ".format(bin_path)
#        cmd += " cut -d \" \" -f 1 | sort | uniq | wc -l"
#        num_readelf_funcs = int(system(cmd))
    num_funcs = (num_orig_funcs, num_code_funcs, num_src_funcs, num_pack_funcs,
                 num_sub_funcs, num_oracle_funcs, num_readelf_funcs)
    return pack_name, bin_path, num_funcs, names, sources


# inevitably use globals since it is fast.
def _init_oracle(oracle):
    global g_oracle
    g_oracle = oracle


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

    pack_bins = {}
    for bin_path in bins:
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        if package not in pack_bins:
            pack_bins[package] = []
        pack_bins[package].append(bin_path)

    result = {}
    logger.info("Processing %d binaries ...", len(bins))
    t0 = time.time()
    for package, bin_list in pack_bins.items():
        logger.info("Processing %d binaries in %s ...", len(bin_list), package)
        numbers = do_multiprocess(
            filter_funcs, bin_list, chunk_size=opts.chunk_size,
            threshold=opts.threshold
        )
        numbers.sort()

        # build oracle to pick functions uniquely.
        oracle = {}
        done = {}
        for data in numbers:
            pack_name, bin_path, num_funcs, names, sources = data
            package, compiler, arch, opti, bin_name = parse_fname(bin_path)
            if pack_name not in oracle:
                oracle[pack_name] = {}
                done[pack_name] = set()
            if bin_name not in oracle[pack_name]:
                oracle[pack_name][bin_name] = {}
            # sources = (source file, source line)
            new_sources = sources - done[pack_name]
            for src_file, src_line in new_sources:
                if src_file not in oracle[pack_name][bin_name]:
                    oracle[pack_name][bin_name][src_file] = set()
                oracle[pack_name][bin_name][src_file].add(src_line)
            done[pack_name].update(new_sources)

        numbers = do_multiprocess(
            filter_funcs, bin_list, chunk_size=opts.chunk_size,
            threshold=opts.threshold, initializer=_init_oracle,
            initargs=(oracle,),
        )
        numbers.sort()

        for data in numbers:
            pack_name, bin_path, num_funcs, names, sources = data
            #num_orig_funcs, num_code_funcs, num_src_funcs, num_pack_funcs, num_sub_funcs, num_oracle_funcs = num_funcs
            if pack_name not in result:
                result[pack_name] = [0 for _ in num_funcs]
            for idx, n in enumerate(num_funcs):
                result[pack_name][idx] += n
    logger.info("done. (%0.3fs)", (time.time() - t0))

    for pack_name, num_funcs in sorted(result.items()):
        s = '{}'.format(pack_name)
        for num in num_funcs:
            s += ',{}'.format(num)
        print(s)
    s = 'Total'
    for num in map(sum, zip(*result.values())):
        s += ',{}'.format(num)
    print(s)
