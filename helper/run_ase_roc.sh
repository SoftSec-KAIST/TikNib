#!/bin/bash
set -x

source config/path_variables.py

# You can run below commands in parallel.
echo "Testing Presemantic features ..."
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase1_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_ase1.yml"
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase2_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_ase2.yml"
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase3_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_ase3.yml"
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase4_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_ase4.yml"

echo "Testing Type features ..."
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase1_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_type_ase1.yml"
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase2_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_type_ase2.yml"
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase3_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_type_ase3.yml"
python helper/test_roc.py \
  --input_list "${BINKIT_DATASET}/ase4_debug.txt" \
  --train_funcs_limit 200000 \
  --config "config/ase18/config_type_ase4.yml"
