#!/bin/bash
set -x

declare -a input_list=(
  "/home/dongkwan/binkit-dataset/gnu_debug.txt"
  "/home/dongkwan/binkit-dataset/gnu_debug_sizeopt.txt"
  "/home/dongkwan/binkit-dataset/gnu_debug_pie.txt"
  "/home/dongkwan/binkit-dataset/gnu_debug_noinline.txt"
  "/home/dongkwan/binkit-dataset/gnu_debug_lto.txt"
  "/home/dongkwan/binkit-dataset/gnu_debug_obfus.txt"
)
source_list="/home/dongkwan/binkit-dataset/gnu_source_list.txt"
ctags_dir="/home/dongkwan/binkit-dataset/gnu_ctags_data"

for f in "${input_list[@]}"
do
  echo "Processing ${f} ..."
  python helper/do_idascript.py \
    --idapath "/home/dongkwan/.tools/ida-6.95" \
    --idc "/home/dongkwan/tiknib/tiknib/ida/fetch_funcdata.py" \
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
