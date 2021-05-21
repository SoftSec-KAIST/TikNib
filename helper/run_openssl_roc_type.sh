#!/bin/bash
set -x

declare -a input_list=(
  "config/openssl/config_openssl_all_type.yml"
  "config/openssl/config_openssl_arm_mips_type.yml"
  "config/openssl/config_openssl_arm_x86_type.yml"
  "config/openssl/config_openssl_mips_arm_type.yml"
  "config/openssl/config_openssl_mips_x86_type.yml"
  "config/openssl/config_openssl_x86_arm_type.yml"
  "config/openssl/config_openssl_x86_mips_type.yml"
)
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  # this is feature selecting for openssl, so we use gnu normal dataset
  python helper/test_roc.py \
    --input_list "/home/dongkwan/binkit-dataset/gnu_debug.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done
