#!/bin/bash
set -x

declare -a input_list=(
  # This one is for processing all functions.
  "/home/dongkwan/binkit-dataset/ase_debug.txt"
  # Then, for experiment and counting, we utilize them separately.
#  "/home/dongkwan/binkit-dataset/ase1_debug.txt"
#  "/home/dongkwan/binkit-dataset/ase2_debug.txt"
#  "/home/dongkwan/binkit-dataset/ase3_debug.txt"
#  "/home/dongkwan/binkit-dataset/ase4_debug.txt"
)

source_list="/home/dongkwan/binkit-dataset/ase_source_list.txt"
ctags_dir="/home/dongkwan/binkit-dataset/ase_ctags_data"

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/do_idascript.py \
    --idapath "/home/dongkwan/.tools/ida-6.95" \
    --idc "/home/dongkwan/tiknib/tiknib/ida/fetch_funcdata_v6.95.py" \
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

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/extract_features.py \
    --input_list "${f}" \
    --threshold 1
done
