#!/bin/bash
set -x

source config/path_variables.py

declare -a input_list=(
  "config/gnu_lto/config_gnu_normal_others_lto_clang4.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_clang5.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_clang6.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_clang7.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_gcc4.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_gcc5.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_gcc6.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_gcc7.yml"
  "config/gnu_lto/config_gnu_normal_others_lto_gcc8.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_lto.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done

declare -a input_list=(
  "config/gnu_noinline/config_gnu_normal_others_noinline_O1.yml"
  "config/gnu_noinline/config_gnu_normal_others_noinline_O2.yml"
  "config/gnu_noinline/config_gnu_normal_others_noinline_O3.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_noinline.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done
