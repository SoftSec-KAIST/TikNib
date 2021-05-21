#!/bin/bash
set -x

declare -a input_list=(
  "config/openssl_topk/config_topk_openssl.yml"
)
for f in "${input_list[@]}"
do
  # this is feature selecting for openssl, so we use gnu normal dataset
  echo "Processing ${f} ..."
  python helper/test_topk.py \
    --input_list "/home/dongkwan/binkit-dataset/ase4_debug_openssl.txt" \
    --train_funcs_limit 200000 \
    --config "${f}"

  # We specified the name of the pickle file that has the cached results of the
  # test_topk.py
  python helper/get_topk_result.py \
    --config "${f}" \
    --pickle "./results/config_topk_openssl/2021-07-19 15:56:43.763949/top-k_tls1_process_heartbeat.pickle"
done

