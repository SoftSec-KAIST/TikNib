#!/bin/bash
echo "Processing IDA analysis ..."
python3 helper/do_idascript.py \
    --idapath "/home/dongkwan/.tools/ida-6.95" \
    --idc "tiknib/ida/fetch_funcdata.py" \
    --input_list "example/input_list_find.txt" \
    --log

echo "Extracting function types ..."
python3 helper/extract_functype.py \
    --source_list "example/source_list.txt" \
    --input_list "example/input_list_find.txt" \
    --ctags_dir "data/ctags" \
    --threshold 1

echo "Extracting features ..."
python3 helper/extract_features.py \
    --input_list "example/input_list_find.txt" \
    --threshold 1

echo "Testing features ..."
python3 helper/test_roc.py \
    --input_list "example/input_list_find.txt" \
    --config "config/gnu/config_gnu_normal_all.yml"
