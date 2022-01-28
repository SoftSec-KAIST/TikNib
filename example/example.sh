#!/bin/bash

source config/path_variables.py

SECONDS=0
echo "Processing IDA analysis ..."
python3 helper/do_idascript.py \
    --idapath "${IDA_PATH}" \
    --idc "${IDA_FETCH_FUNCDATA}" \
    --input_list "example/input_list_find.txt" \
    --log


echo "Extract source file names and line numbers... ${SECONDS}s"
python3 helper/extract_lineno.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1


echo "Filtering functions... ${SECONDS}s"
python3 helper/filter_functions.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1


echo "Counting functions..."
python3 helper/count_functions.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1


echo "Extracting function types ... ${SECONDS}s"
python3 helper/extract_functype.py \
    --source_list "example/source_list.txt" \
    --input_list "example/input_list_find.txt" \
    --ctags_dir "data/ctags" \
    --threshold 1

echo "Extracting features ... ${SECONDS}s"
python3 helper/extract_features.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1

echo "Testing features ... ${SECONDS}s"
python3 helper/test_roc.py \
    --input_list "example/input_list_find.txt" \
    --config "config/gnu/config_gnu_normal_all.yml"
