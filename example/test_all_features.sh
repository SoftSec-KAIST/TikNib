#!/bin/bash
declare -a config_list=(
    "config/gnu/config_gnu_normal_all.yml"
    "config/gnu/config_gnu_normal_arch_all.yml"
    "config/gnu/config_gnu_normal_arch_arm_mips.yml"
    "config/gnu/config_gnu_normal_arch_bits.yml"
    "config/gnu/config_gnu_normal_arch_endian.yml"
    "config/gnu/config_gnu_normal_arch_x86_32-mipseb_64.yml"
    "config/gnu/config_gnu_normal_arch_x86_arm.yml"
    "config/gnu/config_gnu_normal_arch_x86_mips.yml"
    "config/gnu/config_gnu_normal_comp_all.yml"
    "config/gnu/config_gnu_normal_comp_clang4-gcc8.yml"
    "config/gnu/config_gnu_normal_comp_clang.yml"
    "config/gnu/config_gnu_normal_comp_gcc4-clang7.yml"
    "config/gnu/config_gnu_normal_comp_gcc-clang.yml"
    "config/gnu/config_gnu_normal_comp_gcc.yml"
    "config/gnu/config_gnu_normal_hard.yml"
    "config/gnu/config_gnu_normal_obfus_all.yml"
    "config/gnu/config_gnu_normal_obfus_bcf.yml"
    "config/gnu/config_gnu_normal_obfus_fla.yml"
    "config/gnu/config_gnu_normal_obfus_hard.yml"
    "config/gnu/config_gnu_normal_obfus_sub.yml"
    "config/gnu/config_gnu_normal_opti_all_Os.yml"
    "config/gnu/config_gnu_normal_opti_O0-O3.yml"
    "config/gnu/config_gnu_normal_opti_O0-Os.yml"
    "config/gnu/config_gnu_normal_opti_O0toO3.yml"
    "config/gnu/config_gnu_normal_opti_O1-O2.yml"
    "config/gnu/config_gnu_normal_opti_O1-Os.yml"
    "config/gnu/config_gnu_normal_opti_O2-O3.yml"
    "config/gnu/config_gnu_normal_opti_O2-Os.yml"
    "config/gnu/config_gnu_normal_opti_O3-Os.yml"
    "config/gnu/config_gnu_normal_others_lto_hard.yml"
    "config/gnu/config_gnu_normal_others_lto.yml"
    "config/gnu/config_gnu_normal_others_noinline_from_O1_hard.yml"
    "config/gnu/config_gnu_normal_others_noinline_from_O1.yml"
    "config/gnu/config_gnu_normal_others_noinline.yml"
    "config/gnu/config_gnu_normal_others_pie_hard.yml"
    "config/gnu/config_gnu_normal_others_pie.yml"
    "config/gnu/config_gnu_normal_all_type.yml"
    "config/gnu/config_gnu_normal_arch_all_type.yml"
    "config/gnu/config_gnu_normal_arch_arm_mips_type.yml"
    "config/gnu/config_gnu_normal_arch_bits_type.yml"
    "config/gnu/config_gnu_normal_arch_endian_type.yml"
    "config/gnu/config_gnu_normal_arch_x86_32-mipseb_64_type.yml"
    "config/gnu/config_gnu_normal_arch_x86_arm_type.yml"
    "config/gnu/config_gnu_normal_arch_x86_mips_type.yml"
    "config/gnu/config_gnu_normal_comp_all_type.yml"
    "config/gnu/config_gnu_normal_comp_clang4-gcc8_type.yml"
    "config/gnu/config_gnu_normal_comp_clang_type.yml"
    "config/gnu/config_gnu_normal_comp_gcc4-clang7_type.yml"
    "config/gnu/config_gnu_normal_comp_gcc-clang_type.yml"
    "config/gnu/config_gnu_normal_comp_gcc_type.yml"
    "config/gnu/config_gnu_normal_hard_type.yml"
    "config/gnu/config_gnu_normal_obfus_all_type.yml"
    "config/gnu/config_gnu_normal_obfus_bcf_type.yml"
    "config/gnu/config_gnu_normal_obfus_fla_type.yml"
    "config/gnu/config_gnu_normal_obfus_hard_type.yml"
    "config/gnu/config_gnu_normal_obfus_sub_type.yml"
    "config/gnu/config_gnu_normal_opti_all_Os_type.yml"
    "config/gnu/config_gnu_normal_opti_O0-O3_type.yml"
    "config/gnu/config_gnu_normal_opti_O0-Os_type.yml"
    "config/gnu/config_gnu_normal_opti_O0toO3_type.yml"
    "config/gnu/config_gnu_normal_opti_O1-O2_type.yml"
    "config/gnu/config_gnu_normal_opti_O1-Os_type.yml"
    "config/gnu/config_gnu_normal_opti_O2-O3_type.yml"
    "config/gnu/config_gnu_normal_opti_O2-Os_type.yml"
    "config/gnu/config_gnu_normal_opti_O3-Os_type.yml"
    "config/gnu/config_gnu_normal_others_lto_hard_type.yml"
    "config/gnu/config_gnu_normal_others_lto_type.yml"
    "config/gnu/config_gnu_normal_others_noinline_from_O1_hard_type.yml"
    "config/gnu/config_gnu_normal_others_noinline_from_O1_type.yml"
    "config/gnu/config_gnu_normal_others_noinline_type.yml"
    "config/gnu/config_gnu_normal_others_pie_hard_type.yml"
    "config/gnu/config_gnu_normal_others_pie_type.yml"
)

for conf in "${config_list[@]}"
do
    echo "==== Testing ${conf} ==="
    python3 helper/test_roc.py \
        --config "${conf}" \
        --input_list example/input_list_find.txt
done
