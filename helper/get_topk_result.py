import time
import random
import itertools

# import gc
import os
import sys
import datetime
import numpy as np
import yaml
import pickle

from operator import itemgetter
from optparse import OptionParser
from sklearn.model_selection import KFold
from sklearn.metrics import roc_curve, auc, average_precision_score

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.utils import do_multiprocess, parse_fname
from tiknib.utils import load_func_data
from tiknib.utils import flatten
from tiknib.utils import store_cache
from tiknib.utils import load_cache
from get_roc_graph import plot_roc_all

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO)
coloredlogs.install(level=logging.DEBUG)
np.seterr(divide="ignore", invalid="ignore")


def debughere():
    import ipdb; ipdb.set_trace(sys._getframe().f_back)


def get_package(func_key):
    return func_key[0]


def get_binary(func_key):
    return func_key[1]


def get_func(func_key):
    return (func_key[2], func_key[3])


def get_opti(option_key):
    return option_key[0]


def get_arch(option_key):
    return option_key[1]


def get_arch_nobits(option_key):
    return option_key[1].split("_")[0]


def get_bits(option_key):
    return option_key[1].split("_")[1]


def get_compiler(option_key):
    return option_key[2]


def get_others(option_key):
    return option_key[3]


def parse_other_options(bin_path):
    other_options = ["lto", "pie", "noinline"]
    for opt in other_options:
        if opt in bin_path:
            return opt
    return "normal"


def get_optionidx_map(options):
    return {opt: idx for idx, opt in enumerate(sorted(options))}


def is_valid(dictionary, s):
    return s in dictionary and dictionary[s]


def load_options(config):
    options = ["opti", "arch", "compiler", "others"]
    src_options = []
    dst_options = []
    fixed_options = []
    for idx, opt in enumerate(options):
        src_options.append(config["src_options"][opt])
        dst_options.append(config["dst_options"][opt])
        if is_valid(config, "fixed_options") and opt in config["fixed_options"]:
            fixed_options.append(idx)
    src_options = set(itertools.product(*src_options))
    dst_options = set(itertools.product(*dst_options))
    options = sorted(src_options.union(dst_options))
    optionidx_map = get_optionidx_map(options)

    dst_options_filtered = {}
    # Filtering dst options
    for src_option in src_options:

        def _check_option(opt):
            if opt == src_option:
                return False
            for idx in fixed_options:
                if opt[idx] != src_option[idx]:
                    return False
            return True

        candidates = list(filter(_check_option, dst_options))

        # arch needs more filtering ...
        # - 32 vs 64 bits
        # - little vs big endian
        # need to have same archs without bits
        # TODO: move this file name checking into config option.
        if "arch_bits" in config["fname"]:

            def _check_arch_without_bits(opt):
                return get_arch_nobits(opt) == get_arch_nobits(src_option)

            candidates = list(filter(_check_arch_without_bits, candidates))
        # need to have same bits
        elif "arch_endian" in config["fname"]:

            def _check_bits(opt):
                return get_bits(opt) == get_bits(src_option)

            candidates = list(filter(_check_bits, candidates))
        candidates = list(set([optionidx_map[opt] for opt in candidates]))
        dst_options_filtered[optionidx_map[src_option]] = candidates

    logger.info("total %d options.", len(options))
    logger.info("%d src options.", len(src_options))
    logger.info("%d dst options.", len(dst_options))
    logger.info("%d filtered dst options.", len(dst_options_filtered))
    return options, dst_options_filtered


def pre_k(ranks, k):
    count = 0
    for r in ranks:
        if r <= k:
            count += 1
    return count / len(ranks)



def analyze_top_k_results(config, all_data):
    for target_key in all_data:
        logger.info("Analyzing %s", target_key)
        all_ranks=[]
        all_funcs=[]
        for target_option in all_data[target_key]:
            result_arch, result, scores = all_data[target_key][target_option]
            ranks, func_counts, other_ranks = result_arch
            ranks = list(ranks.values())
            func_counts = list(func_counts.values())
            logger.info("Top-K  %s(%s)", target_key, target_option)
            logger.info("Avg Rank: %0.4f", np.mean(ranks))
            logger.info("Std Rank: %0.4f", np.std(ranks))
            logger.info("Prec Top 1: %0.4f", pre_k(ranks,1))
            logger.info("Prec Top 10: %0.4f", pre_k(ranks,10))
            logger.info("Prec Top 100: %0.4f", pre_k(ranks,100))
            logger.info("Avg Counts: %0.4f", np.mean(func_counts))
            all_ranks.extend(ranks)
            all_funcs.extend(func_counts)
        logger.info("Top-K %s", target_key)
        logger.info("Avg Rank: %0.4f", np.mean(all_ranks))
        logger.info("Std Rank: %0.4f", np.std(all_ranks))
        logger.info("Prec Top 1: %0.4f", pre_k(all_ranks,1))
        logger.info("Prec Top 10: %0.4f", pre_k(all_ranks,10))
        logger.info("Prec Top 100: %0.4f", pre_k(all_ranks,100))
        logger.info("Avg Counts: %0.4f", np.mean(all_funcs))
    logger.info("============= normal feature set=============")
    for target_key in all_data:
        logger.info("Analyzing %s", target_key)
        all_ranks=[]
        all_funcs=[]
        for target_option in all_data[target_key]:
            result_arch, result, scores = all_data[target_key][target_option]
            ranks, func_counts, other_ranks = result
            ranks = list(ranks.values())
            func_counts = list(func_counts.values())
            logger.info("Top-K  %s(%s)", target_key, target_option)
            logger.info("Avg Rank: %0.4f", np.mean(ranks))
            logger.info("Std Rank: %0.4f", np.std(ranks))
            logger.info("Prec Top 1: %0.4f", pre_k(ranks,1))
            logger.info("Prec Top 10: %0.4f", pre_k(ranks,10))
            logger.info("Prec Top 100: %0.4f", pre_k(ranks,100))
            logger.info("Avg Counts: %0.4f", np.mean(func_counts))
            all_ranks.extend(ranks)
            all_funcs.extend(func_counts)
        logger.info("Top-K %s", target_key)
        logger.info("Avg Rank: %0.4f", np.mean(all_ranks))
        logger.info("Std Rank: %0.4f", np.std(all_ranks))
        logger.info("Prec Top 1: %0.4f", pre_k(all_ranks,1))
        logger.info("Prec Top 10: %0.4f", pre_k(all_ranks,10))
        logger.info("Prec Top 100: %0.4f", pre_k(all_ranks,100))
        logger.info("Avg Counts: %0.4f", np.mean(all_funcs))

def check_opt(ops, option):
    if type(ops) is not list:
        ops = [ops]
    for op in ops:
        pass

def analyze_opt(data, op1, op2, arch=True):
    global interested_func_keys
    all_ranks=[]
    all_funcs=[]
    all_other={}
    max_ranks=[]
    if type(op1) is not list:
        op1 = [op1]
    if type(op2) is not list:
        op2 = [op2]
    for target_option in data:
        if any([o not in str(target_option) for o in op1]):
            continue
        result_arch, result, scores = data[target_option]
        if arch:
            ranks, funcs, other_ranks = result_arch
        else:
            ranks, funcs, other_ranks = result
        for src_option in ranks:
            tmp_ranks = []
            if any([o not in str(src_option) for o in op2]):
                continue
            all_ranks.append(ranks[src_option])
            all_funcs.append(funcs[src_option])
            tmp_ranks.append(ranks[src_option])
            for f in other_ranks[src_option]:
                if f in all_other:
                    all_other[f].append(other_ranks[src_option][f])
                else:
                    all_other[f] = [other_ranks[src_option][f]]
                tmp_ranks.append(other_ranks[src_option][f])
            max_ranks.append(min(tmp_ranks))
    result=[]
    #result.append('%s to %s'%(op1[0],op2[0]))
    result.append(op1[0])
    result.append(op2[0])
    result.append(str(len(all_ranks)))
    result.append(np.mean(all_funcs))
    result.append(np.mean(all_ranks))
    result.append(pre_k(all_ranks, 1))
    for f in interested_func_keys:
        result.append(np.mean(all_other[f]))
    result.append(np.mean(max_ranks))
    result.append(pre_k(max_ranks, 1))

    '''
    print("%0.3f"% np.mean(all_ranks))
    print("%0.3f"% np.std(all_ranks))
    print("%0.3f"% np.mean(all_funcs))
    print("%0.3f"% pre_k(all_ranks,1))
    #print("%0.3f"% pre_k(all_ranks,10))
    #print("%0.3f"% pre_k(all_ranks,100))
    for f in interested_func_keys:
        print(f[3])
        print("%0.3f"% np.mean(all_other[f]))
        #print("%0.3f"% pre_k(all_other[f],1))
        #print("%0.3f"% pre_k(all_other[f],10))
        #print("%0.3f"% pre_k(all_other[f],100))
    print("MAX")
    print("%0.3f"% np.mean(max_ranks))
    print("%0.3f"% np.std(max_ranks))
    print("%0.3f"% pre_k(max_ranks,1))
    print("%0.3f"% pre_k(max_ranks,10))
    print("%0.3f"% pre_k(max_ranks,100))
    '''
    return result



def analyze(opts):
    global interested_func_keys
    config_fname = opts.config
    with open(config_fname, "r") as f:
        config = yaml.safe_load(f)
    config["fname"] = config_fname

    #file_handler = logging.FileHandler(os.path.join(outdir, "log.txt"))
    #logger.addHandler(file_handler)
    logger.info("config file name: %s", config["fname"])

    options, dst_options = load_options(config)
    features = sorted(config["features"])
    target_funcs = config["target_funcs"]
    patched_funcs = config["patched_funcs"]
    target_func_keys = []
    patched_func_keys = []
    for target_func in target_funcs:
        package, bin_name, src_file, src_line = target_func
        func_key = (package, bin_name, src_file, src_line)
        logger.info("Target function: %s", func_key)
        target_func_keys.append(func_key)
    for patched_func in patched_funcs:
        package, bin_name, src_file, src_line = patched_func
        func_key = (package, bin_name, src_file, src_line)
        logger.info("Patched function: %s", func_key)
        patched_func_keys.append(func_key)

    is_all = False
    if "top-k_all" in opts.pickle:
        is_all = True
    else:
        funcname = os.path.basename(opts.pickle)[6:-7]
    with open(opts.pickle, 'rb') as f:
        if is_all:
            all_data = pickle.load(f)
        else:
            all_data = {}
            all_data[funcname] = pickle.load(f)
    analyze_top_k_results(config, all_data)

    #analyze_opt(all_data[funcname], 'normal', 'normal')
    #analyze_opt(all_data[funcname], ['clang-4','x86_64','O1'], ['gcc-4','x86_64','O1'])

    interested_func_keys = [k for k in target_func_keys if k[3] != funcname]
    interested_func_keys += patched_func_keys

    tests = [('norm', 'norm'),
             ('arm','arm'),
             ('arm','mips'),
             ('arm','x86'),
             ('mips','mips'),
             ('mips','arm'),
             ('mips','x86'),
             ('x86','x86'),
             ('x86','arm'),
             ('x86','mips'),
             ('O2','O3'),
             ('O3','O2'),
             ('gcc','clang'),
             ('gcc-4','gcc-8'),
             ('gcc-8','gcc-4'),
             ('clang-4','clang-7'),
             ('clang-7','clang-4')
            ]

    all_res = []
    all_res.append(['X','Y', '# of test', '# of Func', 'Rank', 'Pre@1', 'Rank (dtls)', 'Rank (tls-patched)',
                    'Rank (dtls-patched)', 'Rank', 'Pre@1'])
    idx = 0
    for test in tests:
        A, B = test
        res = analyze_opt(all_data[funcname], A, B)
        #res2 = analyze_opt(all_data[funcname], A, B, False)
        all_res.append(res)


    delim = ','
    for j in range(len(all_res[0])):
        for i in range(len(all_res)):
            if type(all_res[i][j]) is str:
                print(all_res[i][j], end=delim)
            else:
                print("%0.2f"% all_res[i][j], end=delim)
        print('')



if __name__ == "__main__":
    op = OptionParser()
    op.add_option(
        "--config",
        action="store",
        dest="config",
        help="give config file (ex) config/config_default.yml",
    )
    op.add_option(
        "--pickle",
        type="str",
        action="store",
        dest="pickle",
        help="a file containing pickled result"
    )
    op.add_option(
        "--train_funcs_limit",
        type="int",
        action="store",
        dest="train_funcs_limit",
        default=200000,
        help="a number to limit the number of functions in training",
    )
    (opts, args) = op.parse_args()

    if not opts.config:
        op.print_help()
        exit(1)

    analyze(opts)
