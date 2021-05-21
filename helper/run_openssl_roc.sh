#!/bin/bash
set -x

declare -a input_list=(
  "config/openssl/config_openssl_all.yml"
  "config/openssl/config_openssl_arm_mips.yml"
  "config/openssl/config_openssl_arm_x86.yml"
  "config/openssl/config_openssl_mips_arm.yml"
  "config/openssl/config_openssl_mips_x86.yml"
  "config/openssl/config_openssl_x86_arm.yml"
  "config/openssl/config_openssl_x86_mips.yml"
)
for f in "${input_list[@]}"
do
  # this is feature selecting for openssl, so we use gnu normal dataset
  echo "Processing ${f} ..."
  python helper/test_roc.py \
    --input_list "/home/dongkwan/binkit-dataset/gnu_debug.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"
done
