import capstone
from capstone import *
from capstone.arm import *

from tiknib.feature.asm_const import X86_INST_MAP, MIPS_INST_MAP
from tiknib.feature.asm_const import ARM_INST_MAP, ARM64_INST_MAP
from tiknib.feature.asm_const import GRP_NO_MAP, GRP_NAME_MAP
from tiknib.utils import get_arch, get_bytes

from . import Feature


class AsmFeature(Feature):
    """
    # of instructions
    avg. # of instructions
    # of instructions per BB
    avg. # of instructions per BB
    """

    @staticmethod
    def get(f):
        arch = get_arch(f["arch"])
        data = get_bytes(f["bin_path"], f["bin_offset"], f["size"])
        features = {}
        if data:
            res = analyze_insts(data, arch, start_addr=0)
            if res:
                # Currently, do not use consts from here
                group_data, consts = res
                group_cnt = {}
                for inst in group_data:
                    for group_no in inst:
                        if group_no in group_cnt:
                            group_cnt[group_no] += 1
                        else:
                            group_cnt[group_no] = 1

                cfg_size = float(f["cfg_size"])
                num_inst = len(group_data)
                features["inst_num_total"] = num_inst
                features["inst_avg_total"] = num_inst / cfg_size
                for no, cnt in group_cnt.items():
                    cnt = float(cnt)
                    name = GRP_NO_MAP[no]
                    features["inst_num_{0}".format(name)] = cnt
                    features["inst_avg_{0}".format(name)] = cnt / cfg_size

        return features


def init_mapping(arch):
    if arch.startswith("arm"):
        if arch == "arm_32":
            md = Cs(CS_ARCH_ARM, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
            inst_map = ARM_INST_MAP
        elif arch == "arm_64":
            md = Cs(CS_ARCH_ARM64, CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
            inst_map = ARM64_INST_MAP

    elif arch.startswith("mips"):
        if arch == "mips_32":
            md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
        elif arch == "mips_64":
            md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
        elif arch == "mipseb_32":
            md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN)
        elif arch == "mipseb_64":
            md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_BIG_ENDIAN)
        inst_map = MIPS_INST_MAP

    elif arch.startswith("x86"):
        if arch == "x86_32":
            md = Cs(CS_ARCH_X86, CS_MODE_32 + CS_MODE_LITTLE_ENDIAN)
        elif arch == "x86_64":
            md = Cs(CS_ARCH_X86, CS_MODE_64 + CS_MODE_LITTLE_ENDIAN)
        inst_map = X86_INST_MAP

    return md, inst_map


# asm ast n-gram (default)
def analyze_insts(data, arch, start_addr=0):
    if not data:
        return

    group_data = []
    consts = []
    md, inst_map = init_mapping(arch)

    # this is default
    # md.syntax = CS_OPT_SYNTAX_INTEL
    md.detail = True

    for i in md.disasm(data, start_addr):
        groups = inst_map[i.id].copy()
        #        print(hex(i.address), i.mnemonic, i.op_str)
        #        print (arch)
        #        import traceback
        #        traceback.print_exc()
        #        import pdb; pdb.set_trace()

        # Capstone's arm has different instructions ... it does not have
        # separate branch instructions for arm. it only internally sets
        # the CC_AL flag. Therefore, need to check this.
        # https://www.capstone-engine.org/lang_python.html
        if arch.startswith("arm_"):
            # if current instruction has conditional code
            flag = False
            if arch == "arm_32" and i.cc not in [
                capstone.arm.ARM_CC_AL,
                capstone.arm.ARM_CC_INVALID,
            ]:
                flag = True
            elif arch == "arm_64" and i.cc not in [
                capstone.arm64.ARM64_CC_AL,
                capstone.arm64.ARM64_CC_INVALID,
            ]:
                flag = True
            if flag:
                if GRP_NAME_MAP["ctransfer"] in groups:
                    groups.remove(GRP_NAME_MAP["ctransfer"])
                    groups.append(GRP_NAME_MAP["cndctransfer"])

        # Collect consts from arithmetic instructions
        if GRP_NAME_MAP["abs_arith"] in groups:
            for op in i.operands:
                if op.type in [CS_OP_IMM, ARM_OP_CIMM, ARM_OP_PIMM]:
                    consts.append(op.imm)  # immediate value

        # Add common capstone-defined groups
        # capstone do not support arm's ldmfd
        for x in i.groups:
            # call, jmp, ret
            if x in [1, 2, 3]:
                groups.append(x)

        group_data.append(groups)

    return group_data, consts
