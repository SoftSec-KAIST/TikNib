#!/bin/bash -eu
set -x

source config/path_variables.py

declare -a input_list=(
  "config/gnu/config_gnu_normal_all_type.yml"

  "config/gnu/config_gnu_normal_opti_O0-O3_type.yml"
  "config/gnu/config_gnu_normal_opti_O2-O3_type.yml"
  "config/gnu/config_gnu_normal_opti_O0toO3_type.yml"

  "config/gnu/config_gnu_normal_comp_gcc_type.yml"
  "config/gnu/config_gnu_normal_comp_clang_type.yml"
  "config/gnu/config_gnu_normal_comp_gcc-clang_type.yml"
  "config/gnu/config_gnu_normal_comp_all_type.yml"

  "config/gnu/config_gnu_normal_arch_x86_arm_type.yml"
  "config/gnu/config_gnu_normal_arch_x86_mips_type.yml"
  "config/gnu/config_gnu_normal_arch_arm_mips_type.yml"
  "config/gnu/config_gnu_normal_arch_bits_type.yml"
  "config/gnu/config_gnu_normal_arch_endian_type.yml"
  "config/gnu/config_gnu_normal_arch_all_type.yml"

  "config/gnu/config_gnu_normal_hard_type.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/gnu_debug.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done



declare -a input_list=(
  "config/gnu/config_gnu_normal_opti_O0-Os_type.yml"
  "config/gnu/config_gnu_normal_opti_O1-Os_type.yml"
  "config/gnu/config_gnu_normal_opti_O3-Os_type.yml"
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
  "config/gnu/config_gnu_normal_others_lto_type.yml"
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
  "config/gnu/config_gnu_normal_others_noinline_from_O1_type.yml"
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
  "config/gnu/config_gnu_normal_others_pie_type.yml"
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
  "config/gnu/config_gnu_normal_obfus_bcf_type.yml"
  "config/gnu/config_gnu_normal_obfus_fla_type.yml"
  "config/gnu/config_gnu_normal_obfus_sub_type.yml"
  "config/gnu/config_gnu_normal_obfus_all_type.yml"

  "config/gnu/config_gnu_normal_obfus_hard_type.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "${BINKIT_DATASET}/test_obfus.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done
