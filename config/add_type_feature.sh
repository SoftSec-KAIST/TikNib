#!/bin/bash
sed -i ":a;N;$!ba;s/inst_num_misc\n/inst_num_misc\n  - data_mul_arg_type\n  - data_num_args\n  - data_ret_type\n/g" *.yml
