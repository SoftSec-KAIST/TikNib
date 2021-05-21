import time
import random
import itertools

# import gc
import os
import sys
import glob
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
from tiknib.utils import store_cache, load_cache
from get_roc_graph import plot_roc_all

import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO)
coloredlogs.install(level=logging.DEBUG)
np.seterr(divide="ignore", invalid="ignore")

TRIALS=10

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


def calc_ap(X, y):
    return average_precision_score(y, X)


def calc_roc(X, y):
    fpr, tpr, tresholds = roc_curve(y, X, pos_label=1)
    return auc(fpr, tpr)


def calc_tptn_gap(tps, tns):
    return np.mean(np.abs(tps - tns), axis=0)


def relative_difference(a, b):
    max_val = np.maximum(np.absolute(a), np.absolute(b))
    d = np.absolute(a - b) / max_val
    d[np.isnan(d)] = 0  # 0 / 0 = nan -> 0
    d[np.isinf(d)] = 1  # x / 0 = inf -> 1 (when x != 0)
    return d


def relative_distance(X, feature_indices):
    return 1 - (np.sum(X[feature_indices])) / len(feature_indices)


def calc_metric_helper(func_key):
    global g_funcs, g_func_keys, g_options, g_target_key, g_option_idx, g_feature_indices
    func_data = g_funcs[func_key]
    results_arch = []
    results = []
    optionidx_map = get_optionidx_map(g_options)
    #for src_opt, src_func in func_data.items():
    for option in g_options:
        src_option = option
        src_option_idx = optionidx_map[option]
        if src_option_idx not in func_data:
            results.append(0.0)
            results_arch.append(0.0)
            continue
        if src_option_idx == g_option_idx:
            results.append(0.0)
            results_arch.append(0.0)
            continue

        src_func = func_data[src_option_idx]


        dst_option_idx = g_option_idx
        dst_option = g_options[dst_option_idx]
        dst_func = g_funcs[g_target_key][dst_option_idx]

        assert not np.isnan(src_func).any()
        assert not np.isnan(dst_func).any()
        #results.append(1-np.average(relative_difference(src_func, dst_func)))
        rdiff = relative_difference(src_func, dst_func)
        #get pre trained feature indices
        archs = [get_arch_nobits(dst_option), get_arch_nobits(src_option)]
        archs = "_".join(archs)
        rdists = []
        feature_indices = g_feature_indices[archs]
        rdist = relative_distance(rdiff, feature_indices)
        results_arch.append(rdist)
        feature_indices = g_feature_indices['all']
        rdist = relative_distance(rdiff, feature_indices)
        results.append(rdist)
    return func_key, results_arch, results


# inevitably use globals since it is fast.
def _init_calc(funcs, options, target_key, option_idx, feature_indices):
    global g_funcs, g_func_keys, g_options, g_target_key, g_option_idx, g_feature_indices
    g_funcs = funcs
    g_func_keys = sorted(funcs.keys())
    g_options = options
    g_target_key = target_key
    g_option_idx = option_idx
    g_feature_indices = feature_indices


def calc_metric(funcs, options, target_key, option_idx, feature_indices):
    # now select for features. this find local optimum value using hill
    # climbing.
    metric_results = do_multiprocess(
        calc_metric_helper,
        funcs.keys(),
        chunk_size=1,
        threshold=1,
        initializer=_init_calc,
        initargs=(funcs, options, target_key, option_idx, feature_indices),
    )
    func_keys, results_arch, results = zip(*metric_results)
    scores_arch = {}
    scores = {}
    for idx, func_key in enumerate(func_keys):
        scores_arch[func_key] = results_arch[idx]
        scores[func_key] = results[idx]
    return scores_arch, scores



# preprocess possible target options for src option
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


def group_binaries(input_list):
    with open(input_list, "r") as f:
        bin_paths = f.read().splitlines()
    bins = {}
    packages = set()
    for bin_path in bin_paths:
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        others = parse_other_options(bin_path)
        key = (package, bin_name)
        if key not in bins:
            bins[key] = []
        bins[key].append(bin_path)
        packages.add(package)
    logger.info(
        "%d packages, %d unique binaries, total %d binaries",
        len(packages),
        len(bins),
        len(bin_paths),
    )
    return bins, packages


def load_func_features_helper(bin_paths):
    # TODO: handle suffix correctly.
    # returns {function_key: {option_idx: np.array(feature_values)}}
    global g_options, g_features
    func_features = {}
    num_features = len(g_features)
    optionidx_map = get_optionidx_map(g_options)
    for bin_path in bin_paths:
        package, compiler, arch, opti, bin_name = parse_fname(bin_path)
        others = parse_other_options(bin_path)
        option_key = (opti, arch, compiler, others)
        if option_key not in optionidx_map:
            continue
        _, func_data_list = load_func_data(bin_path, suffix="filtered2")
        for func_data in func_data_list:
            # Use only .text functions for testing
            # These are already filtered in filter_functions.py
            if func_data["seg_name"] != ".text":
                continue
            if func_data["name"].startswith("sub_"):
                continue
            #func_key = (package, bin_name, func_data["name"])
            func_key = (package, bin_name, func_data["src_file"],
                        func_data["src_line"])
            func_key = (package, bin_name, func_data["src_file"],
                        func_data["name"])
            option_idx = optionidx_map[option_key]
            if func_key not in func_features:
                func_features[func_key] = {}
            if option_key not in func_features[func_key]:
                func_features[func_key][option_idx] = np.zeros(
                    num_features, dtype=np.float64
                )
            for feature_idx, feature in enumerate(g_features):
                if feature not in func_data["feature"]:
                    continue
                val = func_data["feature"][feature]
                func_features[func_key][option_idx][feature_idx] = val

    return func_features


# inevitably use globals since it is fast.
def _init_load(options, features):
    global g_options, g_features
    g_options = options
    g_features = features


def load_func_features(input_list, options, features):
    grouped_bins, packages = group_binaries(input_list)
    func_features_list = do_multiprocess(
        load_func_features_helper,
        grouped_bins.values(),
        chunk_size=1,
        threshold=1,
        initializer=_init_load,
        initargs=(options, features),
    )
    funcs = {}
    for func_features in func_features_list:
        funcs.update(func_features)
    return funcs

def load_trained_features(features, pre_trained):
    feature_indices = {}
    logging.info("Loading pre-trained features")
    base_path = pre_trained
    archs = ['arm','mips','x86']
    arch_pairs = ['%s_%s'%(a,b) for a in archs for b in archs]
    arch_pairs.append('all')

    for arch in arch_pairs:
        outdir = base_path % arch
        logger.info(outdir)
        cache_dir = sorted(glob.glob("{}/*".format(outdir)))[-1]
        roc_max = 0
        for idx in range(10):
            data = load_cache(fname="data-{}".format(idx), cache_dir=cache_dir)
            feature_data, train_data, test_data, test_roc_data = data
            train_func_keys, train_tps, train_tns, train_opts, train_roc, train_ap, train_time = train_data

            if train_roc > roc_max:
                roc_max = train_roc
                data_features = feature_data[0]
                selected = feature_data[1]
                indices = []
                for f in selected:
                    feature = data_features[f]
                    indices.append(features.index(feature))
                feature_indices[arch] = indices
    #feature_indices['all']=[5]

    logger.info(feature_indices)

    return feature_indices

def _init_rank(func_keys, scores, options, target_key, interested_keys):
    global g_func_keys, g_scores, g_options, g_target_key, g_interested_keys
    g_func_keys = func_keys
    g_scores = scores
    g_options = options
    g_target_key = target_key
    g_interested_keys = interested_keys


def get_rank_helper(src_option):
    global g_func_keys, g_scores, g_options, g_target_key, g_interested_keys
    optionidx_map = get_optionidx_map(g_options)

    src_option_idx = optionidx_map[src_option]
    rank = 0
    funcs = 0
    other_ranks = {}
    target_found = True
    sorted_keys = sorted(g_func_keys, key=lambda k: g_scores[k][src_option_idx], reverse=True)
    sorted_keys = list(filter(lambda k: g_scores[k][src_option_idx]!=0.0, sorted_keys))
    try:
        rank = sorted_keys.index(g_target_key)+1
    except ValueError:
        return None, None, None, None
    funcs=len(sorted_keys)
    #logger.info("Rank at %d", rank)
    for i_func_key in g_interested_keys:
        if i_func_key == g_target_key:
            continue
        try:
            i_rank = sorted_keys.index(i_func_key)+1
            other_ranks[i_func_key] = i_rank
        except ValueError:
            continue
    return src_option, rank, funcs, other_ranks


def get_rank(func_keys, scores, options, target_key, interested_keys, target_option):
    src_options = [ op for op in options if op != target_option]
    metric_results = do_multiprocess(
        get_rank_helper,
        src_options,
        chunk_size=1,
        threshold=1,
        initializer=_init_rank,
        initargs=(func_keys, scores, options, target_key, interested_keys),
    )
    src_option, total_rank, total_funcs, total_other_ranks = zip(*metric_results)
    ranks = {}
    func_counts = {}
    other_ranks = {}
    for idx, option in enumerate(src_option):
        if option == None:
            continue
        ranks[option] = total_rank[idx]
        func_counts[option] = total_funcs[idx]
        other_ranks[option] = total_other_ranks[idx]
    return [ranks, func_counts, other_ranks]


def do_top_k(opts):
    config_fname = opts.config
    with open(config_fname, "r") as f:
        config = yaml.safe_load(f)
    config["fname"] = config_fname

    # setup output directory
    if "outdir" in config and config["outdir"]:
        outdir = config["outdir"]
    else:
        base_name = os.path.splitext(os.path.basename(config_fname))[0]
        outdir = os.path.join("results", base_name)
    date = datetime.datetime.now()
    outdir = os.path.join(outdir, str(date))
    os.makedirs(outdir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(outdir, "log.txt"))
    logger.addHandler(file_handler)
    logger.info("config file name: %s", config["fname"])
    logger.info("output directory: %s", outdir)

    options, dst_options = load_options(config)
    features = sorted(config["features"])
    logger.info("%d features", len(features))
    feature_indices = load_trained_features(features, config["pre_trained"])

    t0 = time.time()
    logger.info("Feature loading ...")
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
    interested_func_keys = target_func_keys + patched_func_keys
    funcs = load_func_features(opts.input_list, options, features)
    num_funcs = sum([len(x) for x in funcs.values()])
    logger.info(
        "%d functions (%d unique).", num_funcs, len(funcs)
    )
    logger.info("Feature loading done. (%0.3fs)", time.time() - t0)

    # =================
    # start
    # =================
    optionidx_map = get_optionidx_map(options)

    func_keys = sorted(funcs.keys())
    t1 = time.time()
    all_data={}
    for target_key in target_func_keys:
        if target_key not in func_keys:
            logger.info("Target %s not found", target_key)
            continue
        logger.info("Testing %s", target_key)
        all_data[target_key] = {}
        for target_option in options:
            logger.info("Testing %s", target_option)
            target_option_idx = optionidx_map[target_option]
            if target_option_idx not in funcs[target_key]:
                continue
            t2 = time.time()
            scores_arch, scores = calc_metric(funcs, options, target_key, target_option_idx, feature_indices)
            logger.info("Calc %s, %s done. (%0.3fs)", target_key, target_option, time.time() - t2)
            t3 = time.time()
            result_arch = get_rank(func_keys, scores_arch, options, target_key, interested_func_keys, target_option)
            result = get_rank(func_keys, scores, options, target_key, interested_func_keys, target_option)
            all_data[target_key][target_option] = [result_arch, result, scores]
            #debughere()
            logger.info("Rank %s, %s done. (%0.3fs)", target_key, target_option, time.time() - t3)
            ranks, func_counts, other_ranks = result_arch
            ranks2, func_counts2, other_ranks2 = result
            for src_option in options:
                if src_option in ranks:
                    logger.info("%s: Rank %.3f over %.3f", src_option, ranks[src_option], func_counts[src_option])
                    logger.info("%s: Rank %.3f over %.3f", src_option, ranks2[src_option], func_counts2[src_option])
            #all_data[target_key][target_option] = [ranks, func_counts, other_ranks]
            #store_cache(all_data[target_key], fname="top-k_%s"%str(target_key[3]), cache_dir=outdir)
        store_cache(all_data[target_key], fname="top-k_%s"%str(target_key[3]), cache_dir=outdir)
    store_cache(all_data, fname="top-k_all", cache_dir=outdir)
    analyze_top_k_results(config, all_data)


def pre_k(ranks, k):
    count = 0
    for r in ranks:
        if r <= k:
            count += 1
    return count / len(ranks)



def log_res(ranks):
    ranks = list(ranks.values())
    func_counts = list(func_counts.values())
    logger.info("Top-K  %s(%s)", target_key, target_option)
    logger.info("Avg Rank: %0.4f", np.mean(ranks))
    logger.info("Std Rank: %0.4f", np.std(ranks))
    logger.info("Prec Top 1: %0.4f", pre_k(ranks,1))
    logger.info("Prec Top 10: %0.4f", pre_k(ranks,10))
    logger.info("Prec Top 100: %0.4f", pre_k(ranks,100))
    logger.info("Avg Counts: %0.4f", np.mean(func_counts))


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






if __name__ == "__main__":
    op = OptionParser()
    op.add_option(
        "--config",
        action="store",
        dest="config",
        help="give config file (ex) config/config_default.yml",
    )
    op.add_option(
        "--input_list",
        type="str",
        action="store",
        dest="input_list",
        help="a file containing a list of input binaries",
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

    do_top_k(opts)
