#!/bin/bash -eu
set -x

source config/path_variables.py

declare -a input_list=(
  "${BINKIT_DATASET}/gnu_debug.txt"
  "${BINKIT_DATASET}/gnu_debug_sizeopt.txt"
  "${BINKIT_DATASET}/gnu_debug_pie.txt"
  "${BINKIT_DATASET}/gnu_debug_noinline.txt"
  "${BINKIT_DATASET}/gnu_debug_lto.txt"
# "${BINKIT_DATASET}/gnu_debug_obfus.txt"
)
source_list="${BINKIT_DATASET}/gnu_source_list.txt"
ctags_dir="${BINKIT_DATASET}/gnu_ctags_data"

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/do_idascript.py \
    --idapath "${IDA_PATH}" \
    --idc "${IDA_FETCH_FUNCDATA}" \
    --input_list "${f}" \
    --log
done

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_lineno.py \
    --input_list "${f}" \
    --threshold 1
done

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/filter_functions.py \
    --input_list "${f}" \
    --threshold 1
done

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/count_functions.py \
    --input_list "${f}" \
    --threshold 1
done

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_functype.py \
    --source_list "${source_list}" \
    --input_list "${f}" \
    --ctags_dir "${ctags_dir}" \
    --threshold 1
done

# needs to adjust 'pool_size' for the obfuscation dataset because it takes too
# much memory.
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_features.py \
    --input_list "${f}" \
    --threshold 1
done
