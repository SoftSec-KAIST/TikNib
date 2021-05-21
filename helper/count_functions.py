import os
import sys
import time
from optparse import OptionParser

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.utils import do_multiprocess
from tiknib.utils import load_func_data
from tiknib.utils import parse_fname
from tiknib.utils import system

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO)


def plot_data(o_fname, num_funcs, num_bbs):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use('seaborn-white')
    plt.rcParams['font.size'] = 30
    plt.rcParams['axes.labelsize'] = 30
    plt.rcParams['axes.titlesize'] = 30
    plt.rcParams['xtick.labelsize'] = 20
    plt.rcParams['ytick.labelsize'] = 20
    plt.rcParams['legend.fontsize'] = 20
    plt.rcParams['figure.titlesize'] = 20
    plt.rcParams['errorbar.capsize'] = 5

    opti_list = sorted(set(map(lambda x: x[0], num_funcs.keys())))
    options = sorted(set(map(lambda x: (x[1], x[2]), num_funcs.keys())))
    pos = np.arange(len(options))
    colors = ['orangered', 'peru', 'yellowgreen', 'c', 'mediumorchid']
    colors = ['#e6b8af', '#fce5cd', '#d9ead3', '#c9daf8', '#d9d2e9']
    colors = ['red', 'g', 'b', 'c', 'k']
    bars = []
    width = 0.15
    alpha = 0.5

    # Plotting the bars
    fig, ax = plt.subplots(figsize=(14,10))

    for opti_idx, opti in enumerate(opti_list):
        bar_data = []
        for option in options:
            arch, compiler = option
            bar_data.append(num_funcs[(opti, arch, compiler)])

        bars.append(ax.bar(pos + opti_idx * width,
                           bar_data,
                           width,
                           alpha=alpha,
                           color=colors[opti_idx],
                           label=opti))


    ax.set_ylabel('Number of Functions')
    ax.set_ylim([5 * pow(10, 3), 5 * pow(10, 4)])


    ax2 = ax.twinx()
    for option_idx, option in enumerate(options):
        arch, compiler = option
        line_data = []
        for opti_idx, opti in enumerate(opti_list):
            rec = bars[opti_idx][option_idx]
            h = rec.get_height()
            x = rec.get_x() + rec.get_width()/2.0
            line_data.append(num_bbs[(opti, arch, compiler)])
        le = ax2.plot([pos[option_idx] + opti_idx * width \
                  for opti_idx in range(len(opti_list))],
                 line_data,
                 marker='o',
                 linestyle='-',
                 alpha=alpha,
                 color='black',
                 label='# of bb')

    ax2.set_ylabel('Number of Basic Blocks')
    #ax2.set_ylim([4 * pow(10, 5), 10 * pow(10, 5)])
    #ax2.tick_params('y', colors='r')


    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    plt.legend(lines + [lines2[0]], labels + [labels2[0]],
               frameon=True,
               loc="upper right",
               fancybox=True,
               framealpha=alpha,
               borderpad=1,
               fontsize=18)

    #plt.xticks(pos + 2.0*width,
    plt.xticks(pos + 1.5*width,
               list(map(lambda x:
                        '\n'.join([x[1],
                                   x[0]]),
                        options)))

    plt.setp(ax.xaxis.get_majorticklabels(), fontsize=20, rotation=0,
             horizontalalignment='center')
    plt.setp(ax.yaxis.get_majorticklabels(), fontsize=20)
    plt.setp(ax2.yaxis.get_majorticklabels(), fontsize=20)



    #fig.autofmt_xdate(rotation=30, ha='right')
    fig.tight_layout()

    plt.savefig(o_fname + '.pdf', format='pdf')
    logging.info("output graph at: %s", o_fname + '.pdf')


def count_funcs(bin_path):
    # TODO: handle suffix correctly.
    #bin_path, func_data_list = load_func_data(bin_path)
    bin_path, func_data_list = load_func_data(bin_path, suffix="filtered")

    func_data_list = sorted(func_data_list, key=lambda x: x['name'])
    num_funcs = len(func_data_list)
    num_bbs = sum(map(lambda x: x['cfg_size'], func_data_list))

    return bin_path, num_funcs, num_bbs


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
    (opts, args) = op.parse_args()

    assert opts.input_list

    with open(opts.input_list, "r") as f:
        bins = f.read().splitlines()

    # For debugging
    #bins = list(filter(lambda x: "_find" in x, bins))

    # Fix this function to filter out specific options.
    def filter_bins(bin_path):
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        if compiler not in ["clang-7.0", "gcc-8.2.0"]:
            return False
        return True
    bins = list(filter(filter_bins, bins))

    result = {}
    logger.info("Processing %d binaries ...", len(bins))
    t0 = time.time()
    numbers = do_multiprocess(
        count_funcs, bins, chunk_size=opts.chunk_size,
        threshold=opts.threshold
    )
    logger.info("done. (%0.3fs)", (time.time() - t0))

    filtered_num_funcs = {}
    filtered_num_bbs = {}
    for data in numbers:
        bin_path, num_funcs, num_bbs = data
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        if arch.endswith("_64"):
            continue
        if "eb" in arch:
            continue
        #compiler = compiler.split("-")[0]
        key = (opti, arch, compiler)
        if key not in filtered_num_funcs:
            filtered_num_funcs[key] = 0
            filtered_num_bbs[key] = 0
        filtered_num_funcs[key] += num_funcs
        filtered_num_bbs[key] += num_bbs

    plot_data(opts.input_list, filtered_num_funcs, filtered_num_bbs)


    # Do not filter to obtain all data
    total_num_funcs = {}
    total_num_bbs = {}
    for data in numbers:
        bin_path, num_funcs, num_bbs = data
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        compiler = compiler.split("-")[0]
        key = (opti, arch, compiler)
        if key not in total_num_funcs:
            total_num_funcs[key] = 0
            total_num_bbs[key] = 0
        total_num_funcs[key] += num_funcs
        total_num_bbs[key] += num_bbs
    keys = set(map(lambda x: (x[1], x[2]), total_num_funcs.keys()))
    optis = sorted(set(map(lambda x: x[0], total_num_funcs.keys())))
    keys = sorted(keys, key=lambda x: (x[0], x[1]))

    s = "Options,,,,# of Functions,,,,,# of Basic Blocks,,,\n"
    tmp = ["Compiler", "Arch", "Bits"]
    tmp.append("")
    tmp.extend(optis) # for functions
    tmp.append("")
    tmp.extend(optis) # for bbs
    s += ",".join(tmp)
    s += "\n"
    for key in keys:
        arch, compiler = key
        tmp = [compiler.split("-")[0]]
        tmp.extend(arch.split("_"))
        tmp.append("")
        for opti in optis:
            tmp.append(f"\"{total_num_funcs[(opti, arch, compiler)]:,}\"")
        tmp.append("")
        for opti in optis:
            tmp.append(f"\"{total_num_bbs[(opti, arch, compiler)]:,}\"")
        s += ",".join(tmp)
        s += "\n"
    print(s)
