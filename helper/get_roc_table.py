import os
import glob
import sys
import yaml
import re
import numpy as np

from optparse import OptionParser

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.utils import load_cache

import pprint as pp
import logging, coloredlogs
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

def calc_tptn_gap(tps, tns):
    return np.mean(np.abs(tps - tns), axis=0)

def load_results(opts):
    config_list = opts.config_list
    with open(config_list, "r") as f:
        config_fnames = f.read().splitlines()
    config_fnames = list(filter(lambda x: x, config_fnames))

    # First joining features that are selected in all 10-fold validation for at
    # least one test.
    features_union = set()
    all_data = {}
    for config_idx, config_fname in enumerate(config_fnames):
        with open(config_fname, "r") as f:
            config = yaml.safe_load(f)
        config["fname"] = config_fname

        # setup output directory
        if "outdir" in config and config["outdir"]:
            outdir = config["outdir"]
        else:
            base_name = os.path.splitext(os.path.basename(config_fname))[0]
            outdir = os.path.join("results", base_name)

        # select the latest one
        cache_dir = sorted(glob.glob("{}/*".format(outdir)))[-1]

        # TODO: clean up the key name (config_fname to something neat).
        config_key = os.path.basename(config_fname)
        config_key = re.search("config_(.+).yml", config_key).groups()[0]
        all_data[config_key] = []
        features_inter = set()
        for idx in range(10):
            data = load_cache(fname="data-{}".format(idx), cache_dir=cache_dir)
            all_data[config_key].append(data)
            feature_data, train_data, test_data, test_roc_data = data
            features, feature_indices = feature_data
            feature_names = list(map(lambda x: features[x], feature_indices))
            if not features_inter:
                features_inter = set(feature_indices)
            else:
                features_inter.intersection_update(feature_indices)
        features_union.update(features_inter)

    # Create template
    total_data = [[] for _ in range(7)]

    # Now fetch real data
    for config_idx, config_fname in enumerate(config_fnames):
        # TODO: clean up the key name (config_fname to something neat).
        config_key = os.path.basename(config_fname)
        config_key = re.search("config_(.+).yml", config_key).groups()[0]

        rocs = []
        aps = []
        train_times = []
        test_times = []
        num_train_pairs = []
        num_test_pairs = []
        num_features = []
        features_inter = set()
        tptn_gaps = []
        # TODO: print out per-package result
        for idx in range(10):
            data = all_data[config_key][idx]
            feature_data, train_data, test_data, test_roc_data = data
            features, feature_indices = feature_data
            fpr, tpr, thresholds = test_roc_data
            if not features_inter:
                features_inter = set(feature_indices)
            else:
                features_inter.intersection_update(feature_indices)

            train_func_keys, train_tps, train_tns = train_data[:3]
            train_roc, train_ap, train_time = train_data[4:7]
            test_func_keys, test_tps, test_tns = test_data[:3]
            test_roc, test_ap, test_time = test_data[4:7]

            rocs.append(test_roc)
            aps.append(test_ap)
            train_times.append(train_time)
            test_times.append(test_time)
            num_train_pairs.append(len(train_tps) + len(train_tns))
            num_test_pairs.append(len(test_tps) + len(test_tns))
            num_features.append(len(feature_indices))

            tptn_gap = calc_tptn_gap(test_tps, test_tns)
            tptn_gaps.append(tptn_gap)

        # first rows
        total_data[0].append([
            np.mean(num_train_pairs),
            np.mean(num_test_pairs)
        ])

        # second rows
        total_data[1].append([
            np.mean(train_times),
            np.mean(test_times)
        ])

        # third rows
        tmp = {}
        for idx in features_union:
            if idx in features_inter:
                tmp[features[idx]] = [tptn_gap[idx], True]
            else:
                tmp[features[idx]] = [tptn_gap[idx], False]
        total_data[2].append(tmp)

        # fourth row
        total_data[3].append(np.mean(num_features))

        # fifth rows
        total_data[4].append([
            np.mean(tptn_gap),
            np.mean(tptn_gap[list(features_inter)])
        ])

        # sixth rows
        total_data[5].append([
            np.mean(rocs),
            np.std(rocs)
        ])

        # seventh rows
        total_data[6].append([
            np.mean(aps),
            np.std(aps)
        ])

    return config_fnames, total_data, features, features_union


def get_results(opts):
    config_fnames, total_data, features, features_union = load_results(opts)

    # first rows
    print(','.join(map(lambda x:
                       '%.2f' % (x[0] / 1000000.0)
                       if x[0] > 100000
                       else '%.2fF' % (x[0] / 10000), total_data[0])))
    print(','.join(map(lambda x:
                       '%.2f' % (x[1] / 1000000.0)
                       if x[1] > 100000
                       else '%.2fF' % (x[1] / 10000), total_data[0])))

    # second rows
    print(','.join(map(lambda x: '%.1f' % (x[0]), total_data[1])))
    print(','.join(map(lambda x: '%.1f' % (x[1]), total_data[1])))

    # third rows
    for idx in features_union:
        feature = features[idx]
        s = [feature]
        for data in total_data[2]:
            # intersection
            if data[feature][1]:
                s.append('%.2f-' % (data[feature][0]))
            else:
                s.append('%.2f' % (data[feature][0]))
        print(','.join(s))

    # fourth row
    print(','.join(map(lambda x: '%.1f' % (x), total_data[3])))

    # fifth rows
    print(','.join(map(lambda x: '%.2f' % (x[0]), total_data[4])))
    print(','.join(map(lambda x: '%.2f' % (x[1]), total_data[4])))

    # sixth rows
    print(','.join(map(lambda x: '%.2f' % (x[0]), total_data[5])))
    print(','.join(map(lambda x: '%.2f' % (x[1]), total_data[5])))

    # seventh rows
    print(','.join(map(lambda x: '%.2f' % (x[0]), total_data[6])))
    print(','.join(map(lambda x: '%.2f' % (x[1]), total_data[6])))


if __name__ == "__main__":
    op = OptionParser()
    op.add_option(
        "--config_list",
        action="store",
        dest="config_list",
        help="give a file containing a list of config files",
    )
    (opts, args) = op.parse_args()

    if not opts.config_list:
        op.print_help()
        exit(1)

    get_results(opts)
