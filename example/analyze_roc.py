import os
import sys
import yaml

from test_roc import load_options

fnames = [
    "results/config_gnu_normal_all/2020-11-18 13:46:56.393364/data-9.pickle",
    "results/config_gnu_normal_all_type/2020-11-18 15:34:08.325131/data-9.pickle",
    "results/config_gnu_normal_arch_all/2020-11-18 13:53:26.976885/data-9.pickle",
    "results/config_gnu_normal_arch_all_type/2020-11-18 15:40:57.209088/data-9.pickle",
    "results/config_gnu_normal_arch_arm_mips/2020-11-18 13:59:06.807332/data-9.pickle",
    "results/config_gnu_normal_arch_arm_mips_type/2020-11-18 15:52:16.457207/data-9.pickle",
    "results/config_gnu_normal_arch_bits/2020-11-18 14:00:58.467297/data-9.pickle",
    "results/config_gnu_normal_arch_bits_type/2020-11-18 15:54:18.953425/data-9.pickle",
    "results/config_gnu_normal_arch_endian/2020-11-18 14:04:25.204567/data-9.pickle",
    "results/config_gnu_normal_arch_endian_type/2020-11-18 15:58:04.408998/data-9.pickle",
    "results/config_gnu_normal_arch_x86_32-mipseb_64/2020-11-18 14:06:39.619138/data-9.pickle",
    "results/config_gnu_normal_arch_x86_32-mipseb_64_type/2020-11-18 16:00:22.271610/data-9.pickle",
    "results/config_gnu_normal_arch_x86_arm/2020-11-18 14:08:29.490628/data-9.pickle",
    "results/config_gnu_normal_arch_x86_arm_type/2020-11-18 16:02:11.646741/data-9.pickle",
    "results/config_gnu_normal_arch_x86_mips/2020-11-18 14:10:12.834826/data-9.pickle",
    "results/config_gnu_normal_arch_x86_mips_type/2020-11-18 16:04:07.967808/data-9.pickle",
    "results/config_gnu_normal_comp_all/2020-11-18 14:11:57.116225/data-9.pickle",
    "results/config_gnu_normal_comp_all_type/2020-11-18 16:06:00.642131/data-9.pickle",
    "results/config_gnu_normal_comp_clang/2020-11-18 14:20:32.530987/data-9.pickle",
    "results/config_gnu_normal_comp_clang4-gcc8/2020-11-18 14:18:15.595060/data-9.pickle",
    "results/config_gnu_normal_comp_clang4-gcc8_type/2020-11-18 16:12:10.109482/data-9.pickle",
    "results/config_gnu_normal_comp_clang_type/2020-11-18 16:14:24.004042/data-9.pickle",
    "results/config_gnu_normal_comp_gcc/2020-11-18 14:28:42.864321/data-9.pickle",
    "results/config_gnu_normal_comp_gcc4-clang7/2020-11-18 14:22:53.992912/data-9.pickle",
    "results/config_gnu_normal_comp_gcc4-clang7_type/2020-11-18 16:16:51.813816/data-9.pickle",
    "results/config_gnu_normal_comp_gcc-clang/2020-11-18 14:25:15.189431/data-9.pickle",
    "results/config_gnu_normal_comp_gcc-clang_type/2020-11-18 16:18:58.020710/data-9.pickle",
    "results/config_gnu_normal_comp_gcc_type/2020-11-18 16:22:04.013482/data-9.pickle",
    "results/config_gnu_normal_hard/2020-11-18 14:30:51.026836/data-9.pickle",
    "results/config_gnu_normal_hard_type/2020-11-18 16:24:10.376050/data-9.pickle",
    "results/config_gnu_normal_obfus_all/2020-11-18 14:32:11.739096/data-9.pickle",
    "results/config_gnu_normal_obfus_all_type/2020-11-18 16:25:28.413030/data-9.pickle",
    "results/config_gnu_normal_obfus_bcf/2020-11-18 14:34:10.010568/data-9.pickle",
    "results/config_gnu_normal_obfus_bcf_type/2020-11-18 16:27:34.066475/data-9.pickle",
    "results/config_gnu_normal_obfus_fla/2020-11-18 14:36:08.986059/data-9.pickle",
    "results/config_gnu_normal_obfus_fla_type/2020-11-18 16:29:44.656577/data-9.pickle",
    "results/config_gnu_normal_obfus_hard/2020-11-18 14:38:26.912991/data-9.pickle",
    "results/config_gnu_normal_obfus_hard_type/2020-11-18 16:31:48.797762/data-9.pickle",
    "results/config_gnu_normal_obfus_sub/2020-11-18 14:39:46.049780/data-9.pickle",
    "results/config_gnu_normal_obfus_sub_type/2020-11-18 16:33:08.511015/data-9.pickle",
    "results/config_gnu_normal_opti_all_Os/2020-11-18 14:42:18.972945/data-9.pickle",
    "results/config_gnu_normal_opti_all_Os_type/2020-11-18 16:35:41.904540/data-9.pickle",
    "results/config_gnu_normal_opti_O0-O3/2020-11-18 14:48:53.159331/data-9.pickle",
    "results/config_gnu_normal_opti_O0-O3_type/2020-11-18 16:41:32.105557/data-9.pickle",
    "results/config_gnu_normal_opti_O0-Os/2020-11-18 14:51:04.318574/data-9.pickle",
    "results/config_gnu_normal_opti_O0-Os_type/2020-11-18 16:43:20.273041/data-9.pickle",
    "results/config_gnu_normal_opti_O0toO3/2020-11-18 14:53:21.164339/data-9.pickle",
    "results/config_gnu_normal_opti_O0toO3_type/2020-11-18 16:45:26.474475/data-9.pickle",
    "results/config_gnu_normal_opti_O1-O2/2020-11-18 14:58:56.411886/data-9.pickle",
    "results/config_gnu_normal_opti_O1-O2_type/2020-11-18 16:50:15.961717/data-9.pickle",
    "results/config_gnu_normal_opti_O1-Os/2020-11-18 15:01:00.279025/data-9.pickle",
    "results/config_gnu_normal_opti_O1-Os_type/2020-11-18 16:52:14.760052/data-9.pickle",
    "results/config_gnu_normal_opti_O2-O3/2020-11-18 15:03:07.179628/data-9.pickle",
    "results/config_gnu_normal_opti_O2-O3_type/2020-11-18 16:54:16.951183/data-9.pickle",
    "results/config_gnu_normal_opti_O2-Os/2020-11-18 15:05:03.819592/data-9.pickle",
    "results/config_gnu_normal_opti_O2-Os_type/2020-11-18 16:56:05.352433/data-9.pickle",
    "results/config_gnu_normal_opti_O3-Os/2020-11-18 15:07:11.550331/data-9.pickle",
    "results/config_gnu_normal_opti_O3-Os_type/2020-11-18 16:58:03.572961/data-9.pickle",
    "results/config_gnu_normal_others_lto/2020-11-18 15:10:30.730843/data-9.pickle",
    "results/config_gnu_normal_others_lto_hard/2020-11-18 15:09:11.708610/data-9.pickle",
    "results/config_gnu_normal_others_lto_hard_type/2020-11-18 16:59:54.801029/data-9.pickle",
    "results/config_gnu_normal_others_lto_type/2020-11-18 17:01:14.123024/data-9.pickle",
    "results/config_gnu_normal_others_noinline/2020-11-18 15:20:22.294422/data-9.pickle",
    "results/config_gnu_normal_others_noinline_from_O1/2020-11-18 15:17:25.625257/data-9.pickle",
    "results/config_gnu_normal_others_noinline_from_O1_hard/2020-11-18 15:15:46.402218/data-9.pickle",
    "results/config_gnu_normal_others_noinline_from_O1_hard_type/2020-11-18 17:04:08.727242/data-9.pickle",
    "results/config_gnu_normal_others_noinline_from_O1_type/2020-11-18 17:05:29.132283/data-9.pickle",
    "results/config_gnu_normal_others_noinline_type/2020-11-18 17:08:15.539633/data-9.pickle",
    "results/config_gnu_normal_others_pie/2020-11-18 15:26:14.232021/data-9.pickle",
    "results/config_gnu_normal_others_pie_hard/2020-11-18 15:24:42.728424/data-9.pickle",
    "results/config_gnu_normal_others_pie_hard_type/2020-11-18 17:11:47.505651/data-9.pickle",
    "results/config_gnu_normal_others_pie_type/2020-11-18 17:13:05.941983/data-9.pickle",
]

import pickle

for fname in fnames:
    with open(fname, "rb") as f:
        data = pickle.load(f)

    config_fname = fname.split("/")[1]
    if "type" in config_fname:
        continue
    config_fname = os.path.join("config", "gnu", config_fname + ".yml")
    with open(config_fname, "r") as f:
        config = yaml.load(f)
    config["fname"] = config_fname

    # setup output directory
    options, dst_options = load_options(config)

    train_func_keys, train_tps, train_tns, train_opts = data[:4]
    train_roc, train_ap, train_time = data[4:7]
    test_func_keys, test_tps, test_tns, test_opts = data[7:11]
    test_roc, test_ap, test_time = data[11:14]
    features, feature_indices = data[14:16]

    print("=" * 30)
    print(fname)
    print(test_roc)
