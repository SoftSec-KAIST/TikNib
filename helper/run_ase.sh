#!/bin/bash -ue
set -x

source config/path_variables.py

declare -a input_list=(
  # This one is for processing all functions.
  "${BINKIT_DATASET}/ase_debug.txt"
  # Then, for experiment and counting, we utilize them separately.
#  "${BINKIT_DATASET}/ase1_debug.txt"
#  "${BINKIT_DATASET}/ase2_debug.txt"
#  "${BINKIT_DATASET}/ase3_debug.txt"
#  "${BINKIT_DATASET}/ase4_debug.txt"
)

source_list="${BINKIT_DATASET}/ase_source_list.txt"
ctags_dir="${BINKIT_DATASET}/ase_ctags_data"

SECONDS=0
echo "Processing IDA analysis ..."
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/do_idascript.py \
    --idapath "${IDA_PATH}" \
    --idc "${IDA_FETCH_FUNCDATA}" \
    --input_list "${f}" \
    --log
done

echo "Extract source file names and line numbers... ${SECONDS}s"
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_lineno.py \
    --input_list "${f}" \
    --threshold 1
done

echo "Filtering functions... ${SECONDS}s"
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/filter_functions.py \
    --input_list "${f}" \
    --threshold 1
done

echo "Counting functions... ${SECONDS}s"
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/count_functions.py \
    --input_list "${f}" \
    --threshold 1
done

echo "Extracting function types ... ${SECONDS}s"
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_functype.py \
    --source_list "${source_list}" \
    --input_list "${f}" \
    --ctags_dir "${ctags_dir}" \
    --threshold 1
done

echo "Extracting features ... ${SECONDS}s"
for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_features.py \
    --input_list "${f}" \
    --threshold 1
done

echo "DONE in ${SECONDS}s"
