import itertools
import os
import glob
import sys
import time
import numpy as np
import yaml
import re

from optparse import OptionParser
from sklearn.metrics import roc_curve, auc
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(sys.path[0], ".."))
from tiknib.utils import load_cache

import pprint as pp
import logging, coloredlogs
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)


def plot_roc_all(outdir, fprs, tprs):
    # plot all data by key_name
    new_tpr = defaultdict(dict)
    new_fpr = defaultdict(dict)
    new_std = defaultdict(dict)
    new_packages = set()
    for key_name in sorted(tprs.keys()):
        for package in sorted(tprs[key_name].keys()):
            tpr = tprs[key_name][package]
            fpr = fprs[key_name][package]
            trials = sorted(tpr.keys())
            plot_roc(outdir, '%s_%s_10fold' % (key_name.replace('/','.'),
                                              package),
                     tpr, fpr, macro=True)

            if not fpr:
                continue

            new_packages.add(package)

            # this is for std calculation
            all_auc = []

            # First aggregate all false positive rates
            all_fpr = np.unique(np.concatenate([fpr[c] for c in trials]))

            # Then interpolate all ROC curves at this points
            mean_tpr = np.zeros_like(all_fpr)
            all_auc = []
            for c in trials:
                mean_tpr += np.interp(all_fpr, fpr[c], tpr[c])
                all_auc.append(auc(fpr[c], tpr[c]))

            std_auc = np.std(all_auc)

            # Finally average it and compute AUC
            mean_tpr /= len(trials)

            new_tpr[key_name][package] = mean_tpr
            new_fpr[key_name][package] = all_fpr
            new_std[key_name][package] = std_auc


    for package in new_packages:
        tmp_tpr = {}
        tmp_fpr = {}
        tmp_std = {}
        for key_name in new_tpr.keys():
            if package not in new_tpr[key_name]:
                continue

            tmp_tpr[key_name] = new_tpr[key_name][package]
            tmp_fpr[key_name] = new_fpr[key_name][package]
            tmp_std[key_name] = new_std[key_name][package]

        plot_roc(outdir, 'roc_%s' % (package),
                 tmp_tpr, tmp_fpr,
                 std=tmp_std,
                 macro=False)


def plot_roc(outdir, out_fname, tpr, fpr, std=None, macro=True):
    classes = sorted(tpr.keys())
    if isinstance(classes[0], str):
        classes = sorted(classes, key=lambda x: 'type' in x)
    roc_auc = {}

    #for style
    plt.style.use('seaborn-white')
    plt.rcParams['font.size'] = 40
    plt.rcParams['axes.labelsize'] = 40
    plt.rcParams['axes.titlesize'] = 40
    plt.rcParams['xtick.labelsize'] = 40
    plt.rcParams['ytick.labelsize'] = 40
    plt.rcParams['legend.fontsize'] = 30
    plt.rcParams['figure.titlesize'] = 40
    plt.rcParams['errorbar.capsize'] = 5
    #end style

    # Plot all ROC curves
    fig = plt.figure(figsize=(14,10))

    # First aggregate all false positive rates
    all_fpr = np.unique(np.concatenate([fpr[c] for c in classes]))

    colors = itertools.cycle(['#ff0000', '#00ff00', '#0000ff', '#ff00ff',
                              '#00ffff', '#ffff00'])
    markers = itertools.cycle(['s',6,'v','h',7,'o','*'])
    lw = 2

    for c, color, marker in zip(classes, colors, markers):
        inter_tpr = np.interp(all_fpr, fpr[c], tpr[c])
        markevery = int(len(inter_tpr) * 0.25) + 1
        markevery = 0.1
        if macro:
            plt.plot(fpr[c], tpr[c],
                     marker=marker, markevery=markevery, markersize=14,
                     color=color, lw=lw, alpha=0.5,
                     label='{0} (AUC = {1:0.4f})'
                     ''.format(c, auc(fpr[c], tpr[c])))

        else:
            plt.plot(all_fpr, inter_tpr,
                     marker=marker, markevery=markevery, markersize=14,
                     color=color, lw=lw, alpha=0.5,
                     label='{0} (AUC = {1:0.4f} $\pm$ {2:0.4f})'
                     ''.format(c, auc(fpr[c], tpr[c]), std[c]))

    plt.plot([0, 1], [0, 1], 'k--', lw=lw)
    plt.xlim([-0.03, 1.03])
    plt.ylim([-0.03, 1.03])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    #plt.title('Receiver Operating Characteristic of Full Dataset', fontsize=20)
    plt.legend(frameon=True, loc="lower right", fancybox=True, framealpha=.8,
               borderpad=1)

    ax = fig.get_axes()[0]
    #plt.setp(ax.xaxis.get_majorticklabels(), fontsize=20)
    #plt.setp(ax.yaxis.get_majorticklabels(), fontsize=20)
    plt.tight_layout()
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(os.path.join(outdir, out_fname + '.pdf'), format='pdf')
    plt.close(fig)


def print_plots(opts):
    config_list = opts.config_list
    with open(config_list, "r") as f:
        config_fnames = f.read().splitlines()
    config_fnames = list(filter(lambda x: x, config_fnames))

    fprs = {}
    tprs = {}
    for config_fname in config_fnames:
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
        config_key = config_fname
        config_key = re.search("_([^_]+).yml", config_key).groups()[0]
        config_key = config_key.upper()

        # TODO: print out per-package result
        package = "all"
        fprs[config_key] = {package : {}}
        tprs[config_key] = {package : {}}
        for idx in range(10):
            data = load_cache(fname="data-{}".format(idx), cache_dir=cache_dir)
            feature_data, train_data, test_data, test_roc_data = data
            fpr, tpr, thresholds = test_roc_data
            fprs[config_key][package][idx] = fpr
            tprs[config_key][package][idx] = tpr
    plot_roc_all(opts.outdir, fprs, tprs)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option(
        "--config_list",
        action="store",
        dest="config_list",
        help="give a file containing a list of config files",
    )
    op.add_option(
        "--outdir",
        action="store",
        dest="outdir",
        help="give a directory for output",
    )
    (opts, args) = op.parse_args()

    if not opts.config_list:
        op.print_help()
        exit(1)

    print_plots(opts)
