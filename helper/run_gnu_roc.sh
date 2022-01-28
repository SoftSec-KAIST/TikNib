#!/bin/bash
set -x

source config/path_variables.py

declare -a input_list=(
  "config/gnu/config_gnu_normal_all.yml"

  "config/gnu/config_gnu_normal_opti_O0-O3.yml"
  "config/gnu/config_gnu_normal_opti_O2-O3.yml"
  "config/gnu/config_gnu_normal_opti_O0toO3.yml"

  "config/gnu/config_gnu_normal_comp_gcc.yml"
  "config/gnu/config_gnu_normal_comp_clang.yml"
  "config/gnu/config_gnu_normal_comp_gcc-clang.yml"
  "config/gnu/config_gnu_normal_comp_all.yml"

  "config/gnu/config_gnu_normal_arch_x86_arm.yml"
  "config/gnu/config_gnu_normal_arch_x86_mips.yml"
  "config/gnu/config_gnu_normal_arch_arm_mips.yml"
  "config/gnu/config_gnu_normal_arch_bits.yml"
  "config/gnu/config_gnu_normal_arch_endian.yml"
  "config/gnu/config_gnu_normal_arch_all.yml"

  "config/gnu/config_gnu_normal_hard.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/gnu_debug.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done

exit 0


declare -a input_list=(
  "config/gnu/config_gnu_normal_opti_O0-Os.yml"
  "config/gnu/config_gnu_normal_opti_O1-Os.yml"
  "config/gnu/config_gnu_normal_opti_O3-Os.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_size.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done

declare -a input_list=(
  "config/gnu/config_gnu_normal_others_lto.yml"
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
  "config/gnu/config_gnu_normal_others_noinline_from_O1.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_noinline.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done

declare -a input_list=(
  "config/gnu/config_gnu_normal_others_pie.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_pie.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done

declare -a input_list=(
  "config/gnu/config_gnu_normal_obfus_bcf.yml"
  "config/gnu/config_gnu_normal_obfus_fla.yml"
  "config/gnu/config_gnu_normal_obfus_sub.yml"
  "config/gnu/config_gnu_normal_obfus_all.yml"

  "config/gnu/config_gnu_normal_obfus_hard.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_obfus.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done
