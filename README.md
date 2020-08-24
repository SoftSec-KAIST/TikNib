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
paper](https://0xdkay.me/pub/2020/kim-arxiv2020.pdf).

# Dataset
For building the cross-compiling environment and dataset, please check
[here](https://github.com/SoftSec-KAIST/BinKit).

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

### 1. Run IDA Pro to extract preliminary data for each functions.

This step takes the most time. Please configure the `chunk_size` for parallel
processing.

```bash
$ python3 helper/do_idascript.py \
    --idapath "/home/dongkwan/.tools/ida-6.95" \
    --idc "tiknib/ida/fetch_funcdata.py" \
    --input_list "example/input_list_find.txt" \
    --log
```

Additionally, you can use this script to run any idascript in parallel.

### 2. Extract function type information for type features.

```bash
python3 helper/extract_functype.py \
  --source_list "example/source_list.txt" \
  --input_list "example/input_list_find.txt" \
  --ctags_dir "data/ctags" \
  --threshold 1
```

### 3. Extract numeric presemantic features and type features.

```bash
python3 helper/extract_features.py \
  --input_list "example/input_list_find.txt" \
  --threshold 1
```

### 4. Evaluate target configuration

```bash
python3 helper/test_roc.py \
  --input_list "example/input_list_find.txt" \
  --config "config/gnu/config_gnu_normal_all.yml"
```

For more details, please check `example/`. All configuration files for our
experiments are in `config/`.

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
