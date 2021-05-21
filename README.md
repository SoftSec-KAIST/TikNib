# Description
TikNib is a binary code similarity analysis (BCSA) tool. TikNib enables
evaluating the effectiveness of features used in BCSA. One can extend it to
evaluate other interesting features as well as similarity metrics.

Currently, TikNib supports features as listed below. TikNib also employs an
interpretable feature engineering model, which essentially measures the relative
difference between each feature. In other words, it captures how much each
feature differs across different compile options. Note that this model and its
internal similarity scoring metric is not the best approach for addressing BCSA
problems, but it can help analyze how the way of compilation affects each
feature.

TikNib currently focuses on function-level similarity analysis, which is a
fundamental unit of binary analysis.

For more details, please check [our
paper](https://arxiv.org/abs/2011.10749).

# Dataset
For building the cross-compiling environment and dataset, please check
[BinKit](https://github.com/SoftSec-KAIST/BinKit).

# Supported features

### CFG features
- cfg_size
- cfg_avg_degree
- cfg_num_degree
- cfg_avg_loopintersize
- cfg_avg_loopsize
- cfg_avg_sccsize
- cfg_num_backedges
- cfg_num_loops
- cfg_num_loops_inter
- cfg_num_scc
- cfg_sum_loopintersize
- cfg_sum_loopsize
- cfg_sum_sccsize

### CG features
- cg_num_callees
- cg_num_callers
- cg_num_imported_callees
- cg_num_incalls
- cg_num_outcalls
- cg_num_imported_calls

### Instruction features
- inst_avg_abs_dtransfer
- inst_avg_abs_arith
- inst_avg_abs_ctransfer
- inst_num_abs_dtransfer (dtransfer + misc)
- inst_num_abs_arith (arith + shift)
- inst_num_abs_ctransfer (ctransfer + cond ctransfer)
- inst_avg_inst
- inst_avg_floatinst
- inst_avg_logic
- inst_avg_dtransfer
- inst_avg_arith
- inst_avg_cmp
- inst_avg_shift
- inst_avg_bitflag
- inst_avg_cndctransfer
- inst_avg_ctransfer
- inst_avg_misc
- inst_num_inst
- inst_num_floatinst
- inst_num_logic
- inst_num_dtransfer
- inst_num_arith
- inst_num_cmp
- inst_num_shift
- inst_num_bitflag
- inst_num_cndctransfer
- inst_num_ctransfer
- inst_num_misc

### Type features
- data_mul_arg_type
- data_num_args
- data_ret_type

# How to use
TikNib has two parts: ground truth building and feature extraction.

## Scripts Used for Our Evaluation

To see the scripts used in our evaluation, please check the shell scripts under
[/helper](/helper/). For example, [run_gnu.sh](/helper/run_gnu.sh) builds ground
truth and extracts features for GNU packages. Then,
[run_gnu_roc.sh](/helper/run_gnu_roc.sh) computes the ROC AUC for the results.
You have to run these scripts sequentially as the second one utilizes the cached
results obtained from the first one.
We also added top-k results for the OpenSSL package, which is described in
Sec 5.3 in [our paper](https://arxiv.org/abs/2011.10749).
Please check [run_openssl_roc.sh](/helper/run_openssl_roc.sh) and
[run_openssl_roc_topk.sh](/helper/run_openssl_roc_topk.sh) in the same
directory, of which should also be executed sequentially.

## Building Ground Truth
TikNib includes scripts for building ground truth for evaluation, as described
in Sec 3.2 in [our paper](https://arxiv.org/abs/2011.10749). After compiling the
datasets using [BinKit](https://github.com/SoftSec-KAIST/BinKit), we build
ground truth as below.

Given two functions of the same name, we check if they originated from the same
source files and if their line numbers are the same. We also check if both
functions are from the same package and from the binaries of the same name to
confirm their equivalence. Based on these criteria we conducted several steps to
build ground truth and clean the datasets. For more details, please check [our
paper](https://arxiv.org/abs/2011.10749).

### 1. Run IDA Pro to extract preliminary data for each functions.

**This step takes the most time.**

This step fetches preliminary data for the functions in each binary and stores
the data in a `pickle` format. For a given binary, it generates a pickle file on
the same path with a suffix of `.pickle`. Please configure the `chunk_size` for
parallel processing.

For IDA Pro v6.95 (original version in the paper), use
`tiknib/ida/fetch_funcdata.py`.

```bash
$ python helper/do_idascript.py \
    --idapath "/home/dongkwan/.tools/ida-6.95" \
    --idc "tiknib/ida/fetch_funcdata.py" \
    --input_list "example/input_list_find.txt" \
    --log
```

For IDA Pro v7.5, use `tiknib/ida/fetch_funcdata_v7.5.py`.

```bash
$ python helper/do_idascript.py \
    --idapath "/home/dongkwan/.tools/ida-v7.5" \
    --idc "tiknib/ida/fetch_funcdata_v7.5.py" \
    --input_list "example/input_list_find.txt" \
    --log
```

Additionally, **you can use this script to run any idascript for numerous
binaries in parallel.**


### 2. Extract source file names and line numbers to build ground truth.
This extracts source file name and line number by parsing the debugging
information in a given binary. The binary must have been compiled with
the `-g` option.

```bash
$ python helper/extract_lineno.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1
```

### 3. Filter functions.
This filters functions by checking the source file name and line number.
This removes compiler intrinsic functions and duplicate functions spread
over multiple binaries within the same package.

```bash
$ python helper/filter_functions.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1
```

### (Optional) 4. Counting the number of functions.
This counts the number of functions and generates a graph of that function
on the same path of `input_list`. This also prints the numbers separated
by `','`. In the below example, a pdf file containing the graph will be
created in `example/input_list_find.pdf`

```bash
$ python helper/count_functions.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1
```


## Extracting Features

### 1. Run IDA Pro to extract preliminary data for each functions.
This is the exact same step as the one described above.

### 2. Extract function type information for type features.
By utilizing `ctags`, this will extract type information. This will add
`abstract_args_type` and `abstract_ret_type` into the previously created
`.pickle` file.

```bash
$ python helper/extract_functype.py \
    --source_list "example/source_list.txt" \
    --input_list "example/input_list_find.txt" \
    --ctags_dir "data/ctags" \
    --threshold 1
```

For example, for a function type of `mode_change *__usercall@<rax>(const char
*ref_file@<rsi>)` extracted from IDA Pro, it will follow the ctags and
recognizes `mode_change` represents for a custom `struct`. Consequently, it adds
new data as below.

``` python
    'abstract_args_type': ['char *'],
    'abstract_ret_type': 'struct *',
```

### 3. Extract numeric presemantic features and type features.

This extracts numeric presemantic features as stated above.

```bash
$ python helper/extract_features.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1
```

The extracted features will be stored in each `.pickle` file. Below is an
example showing a part of extracted features for the `mode_create_from_ref`
function in the `find` binary in `findutils`.

```python
{
    'package': 'findutils-4.6.0',
    'bin_name': 'find.elf',
    'name': 'mode_create_from_ref',
    'arch': 'x86_64',
    'opti': 'O3',
    'compiler': 'gcc-8.2.0',
    'others': 'normal',
    'func_type': 'mode_change *__usercall@<rax>(const char *ref_file@<rsi>)',
    'abstract_args_type': ['char *'],
    'ret_type': 'mode_change *',
    'abstract_ret_type': 'struct *',
    'cfg': [(0, 1), (0, 2), (1, 2)],
    'cfg_size': 3,
    'feature': {
        'cfg_avg_degree': 2,
        'cfg_avg_indegree': 1,
        'cfg_avg_loopintersize': 0,
        'cfg_avg_loopsize': 0,
        'cfg_avg_outdegree': 1,
        'cfg_avg_sccsize': 1,
        'cfg_max_depth': 2,
        'cfg_max_width': 2,
        'cfg_num_backedges': 0,
        'cfg_num_bfs_edges': 2,
        'cfg_num_degree': 6,
        'cfg_num_indegree': 3,
        'cfg_num_loops': 0,
        'cfg_num_loops_inter': 0,
        'cfg_num_outdegree': 3,
        'cfg_num_scc': 3,
        'cfg_size': 3,
        'cfg_sum_loopintersize': 0,
        'cfg_sum_loopsize': 0,
        'cfg_sum_sccsize': 3,
        'cg_num_callees': 2,
        'cg_num_callers': 0,
        'cg_num_imported_callees': 1,
        'cg_num_imported_calls': 1,
        'cg_num_incalls': 0,
        'cg_num_outcalls': 2,
        'data_avg_abs_strings': 0,
        'data_avg_arg_type': 2,
        'data_avg_consts': 144,
        'data_avg_strlen': 0,
        'data_mul_arg_type': 2,
        'data_num_args': 1,
        'data_num_consts': 1,
        'data_num_strings': 0,
        'data_ret_type': 2,
        'data_sum_abs_strings': 0,
        'data_sum_abs_strings_seq': 0,
        'data_sum_arg_type': 2,
        'data_sum_arg_type_seq': 2,
        'data_sum_consts_seq': 144,
        'data_sum_strlen': 0,
        'data_sum_strlen_seq': 0,
        'inst_avg_abs_arith': 0.6666666666666666,
        'inst_avg_abs_ctransfer': 1.3333333333333333,
        'inst_avg_abs_dtransfer': 4.666666666666667,
        'inst_avg_arith': 0.6666666666666666,
        'inst_avg_bitflag': 0.3333333333333333,
        'inst_avg_cmp': 0.3333333333333333,
        'inst_avg_cndctransfer': 0.3333333333333333,
        'inst_avg_ctransfer': 1.0,
        'inst_avg_dtransfer': 4.666666666666667,
        'inst_avg_grp_call': 0.6666666666666666,
        'inst_avg_grp_jump': 0.3333333333333333,
        'inst_avg_grp_ret': 0.3333333333333333,
        'inst_avg_logic': 0.3333333333333333,
        'inst_avg_total': 7.333333333333333,
        'inst_num_abs_arith': 2.0,
        'inst_num_abs_ctransfer': 4.0,
        'inst_num_abs_dtransfer': 14.0,
        'inst_num_arith': 2.0,
        'inst_num_bitflag': 1.0,
        'inst_num_cmp': 1.0,
        'inst_num_cndctransfer': 1.0,
        'inst_num_ctransfer': 3.0,
        'inst_num_dtransfer': 14.0,
        'inst_num_grp_call': 2.0,
        'inst_num_grp_jump': 1.0,
        'inst_num_grp_ret': 1.0,
        'inst_num_logic': 1.0,
        'inst_num_total': 22
    },
    ...
}
```

### 4. Evaluate target configuration

```bash
$ python helper/test_roc.py \
    --input_list "example/input_list_find.txt" \
    --train_funcs_limit 200000 \
    --config "config/gnu/config_gnu_normal_all.yml"
```

For more details, please check `example/`. All configuration files for our
experiments are in `config/`. The time spent for running `example/example.sh`
took as below.

- Processing IDA analysis: 1384 s
- Extracting function types: 102 s
- Extracting features: 61 s
- Training: 31 s
- Testing: 0.8 s

You can obtain below information after running `test_roc.py`.

```
Features:
inst_num_abs_ctransfer (inter): 0.4749
inst_num_cmp (inter): 0.5500
inst_num_cndctransfer (inter): 0.5906
...
...
...
Avg \# of selected features: 13.0000
Avg. TP-TN Gap: 0.3866
Avg. TP-TN Gap of Grey: 0.4699
Avg. ROC: 0.9424
Std. of ROC: 0.0056
Avg. AP: 0.9453
Std. of AP: 0.0058
Avg. Train time: 30.4179
AVg. Test time: 1.4817
Avg. # of Train Pairs: 155437
Avg. # of Test Pairs: 17270
```

# Issues

### Tested environment
We ran all our experiments on a server equipped with four Intel Xeon E7-8867v4
2.40 GHz CPUs (total 144 cores), 896 GB DDR4 RAM, and 4 TB SSD. We setup Ubuntu
16.04 with IDA Pro v6.95 on the server.

Currently, it works on IDA Pro v6.95 and v7.5 with Python 3.8.0 on the system.

# Authors
This project has been conducted by the below authors at KAIST.
* [Dongkwan Kim](https://0xdkay.me/)
* [Eunsoo Kim](https://hahah.kim)
* [Sang Kil Cha](https://softsec.kaist.ac.kr/~sangkilc/)
* [Sooel Son](https://sites.google.com/site/ssonkaist/home)
* [Yongdae Kim](https://syssec.kaist.ac.kr/~yongdaek/)

# Citation
We would appreciate if you consider citing [our
paper](https://0xdkay.me/pub/2020/kim-arxiv2020.pdf) when using TikNib.
```bibtex
@article{kim:2020:binkit,
  author = {Dongkwan Kim and Eunsoo Kim and Sang Kil Cha and Sooel Son and Yongdae Kim},
  title = {Revisiting Binary Code Similarity Analysis using Interpretable Feature Engineering and Lessons Learned},
  eprint={2011.10749},
  archivePrefix={arXiv},
  primaryClass={cs.SE}
  year = {2020},
}
```
