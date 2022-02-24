# Unknown, but obvserved
PPC_UNKOWN = [
    # condition register _
    'CREQV',
    'CRMOVE',
    'CRNOT',
    'CRSET',
    'MCRF',  # Move Condition Register Field

    'EQV',
    'ISYNC',  # instruction synccccchronize
    # UNKNOWN 64-bit
    'VSEL',
]

# ================= POWERPC 32 =============================================
# data transfer
# reference : https://www.ibm.com/docs/en/aix/7.3?topic=reference-appendix-f-powerpc-instructions
# reference : https://files.openpower.foundation/s/dAYSdGzTfW4j2r2
PPC_GRP_DTRANSFER = [
    # load
    'LA',
    # load byte
    'LBZ', 'LBZCIX', 'LBZU', 'LBZUX', 'LBZX',
    # load double
    'LD', 'LDARX', 'LDBRX', 'LDCIX', 'LDU', 'LDUX', 'LDX',
    # load half
    'LHA', 'LHAU', 'LHAUX', 'LHAX', 'LHBRX',
    'LHZ', 'LHZCIX', 'LHZU', 'LHZUX', 'LHZX',
    # load immediate
    'LI', 'LIS',
    'LMW',
    'LSWI',
    # load vector
    'LVEBX', 'LVEHX', 'LVEWX', 'LVSL', 'LVSR', 'LVX', 'LVXL',
    # load word
    'LWA', 'LWARX', 'LWAUX', 'LWAX', 'LWBRX', 'LWSYNC',
    'LWZ', 'LWZCIX', 'LWZU', 'LWZUX', 'LWZX',
    # load VSX
    'LXSDX', 'LXVD2X', 'LXVDSX', 'LXVW4X',
    # store byte
    'STB', 'STBCIX', 'STBU', 'STBUX', 'STBX',
    # store double
    'STD', 'STDBRX', 'STDCIX', 'STDCX', 'STDU', 'STDUX', 'STDX',
    # store half word
    'STH', 'STHBRX', 'STHCIX', 'STHU', 'STHUX', 'STHX',
    'STMW',
    'STSWI',
    # store vector
    'STVEBX', 'STVEHX', 'STVEWX', 'STVX', 'STVXL',
    # store word
    'STW', 'STWBRX', 'STWCIX', 'STWCX', 'STWU', 'STWUX', 'STWX',
    # store VSX
    'STXSDX', 'STXVD2X', 'STXVW4X',
    'MR',
    # move from
    'MFAMR', 'MFASR',
    'MFBR0', 'MFBR1', 'MFBR2', 'MFBR3', 'MFBR4', 'MFBR5', 'MFBR6', 'MFBR7',
    'MFCFAR', 'MFCR', 'MFCTR',
    'MFDAR', 'MFDBATL', 'MFDBATU', 'MFDCCR', 'MFDCR',
    'MFDEAR', 'MFDSCR', 'MFDSISR',
    'MFESR', 'MFFS', 'MFIBATL', 'MFIBATU', 'MFICCR', 'MFLR', 'MFMSR',
    'MFOCRF', 'MFPID', 'MFPVR', 'MFRTCL', 'MFRTCU',
    'MFSPEFSCR', 'MFSPR', 'MFSR', 'MFSRIN', 'MFSRR2', 'MFSRR3',
    'MFTB', 'MFTBHI', 'MFTBLO', 'MFTBU', 'MFTCR', 'MFVSCR', 'MFXER',
    # move to
    'MTAMR',
    'MTBR0', 'MTBR1', 'MTBR2', 'MTBR3', 'MTBR4', 'MTBR5', 'MTBR6', 'MTBR7',
    'MTCFAR', 'MTCR', 'MTCRF', 'MTCTR',
    'MTDAR', 'MTDBATL', 'MTDBATU', 'MTDCCR', 'MTDCR',
    'MTDEAR', 'MTDSCR', 'MTDSISR',
    'MTESR', 'MTFSB0', 'MTFSB1', 'MTFSF', 'MTFSFI', 'MTIBATL', 'MTIBATU',
    'MTICCR', 'MTLR', 'MTMSR', 'MTMSRD', 'MTOCRF', 'MTPID',
    'MTSPEFSCR', 'MTSPR', 'MTSR', 'MTSRIN', 'MTSRR2', 'MTSRR3',
    'MTTBHI', 'MTTBL', 'MTTBLO', 'MTTBU', 'MTTCR', 'MTVSCR', 'MTXER',

]


PPC_GRP_FLOAT_DTRANSFER = [
    'FMR',
    'LFD', 'LFDU', 'LFDUX', 'LFDX', 'LFIWAX', 'LFIWZX',
    'LFS', 'LFSU', 'LFSUX', 'LFSX',
    'STFD', 'STFDU', 'STFDUX', 'STFDX', 'STFIWX',
    'STFS', 'STFSU', 'STFSUX', 'STFSX',
    # vector merge
    'VMRGHB', 'VMRGLB',
    # vector pack
    'VPKUHUM', 'VPKUWUM',
    # vector permute
    'VPERM',
]

# binary arithmetic instructions:
PPC_GRP_ARITH = [
    'NEG',
    'ADD', 'ADDC', 'ADDE', 'ADDI', 'ADDIC', 'ADDIS', 'ADDME', 'ADDZE',
    'DIVD', 'DIVDU', 'DIVW', 'DIVWU',
    'MULHD', 'MULHDU', 'MULHW', 'MULHWU', 'MULLD', 'MULLI', 'MULLW',
    'SUB', 'SUBC', 'SUBF', 'SUBFC', 'SUBFE', 'SUBFIC', 'SUBFME', 'SUBFZE',
]

# floating point arithmetic instructions
PPC_GRP_FLOAT_ARITH = [
    'FABS',
    'FMADD',
    'FMSUB',
    'FNEG',
    'FADD', 'FADDS', 'FDIV', 'FDIVS', 'FMUL', 'FMULS', 'FSUB', 'FSUBS',
    'FRSP',   # Floating Round to Single-Precision
    'FSQRT',
    # floating convert
    'FCFID',  'FCTIDZ', 'FCTIWZ',
    # vector add
    'VADDUBM', 'VADDUHM', 'VADDUWM',
    # vector multiply
    'VMSUMUHM', 'VMULOUH',
    # vector subtract
    'VSUBUHS', 'VSUBUWM',
]

PPC_GRP_CMP = [
    'CMPB', 'CMPD', 'CMPDI', 'CMPLD', 'CMPLDI',
    'CMPLW', 'CMPLWI', 'CMPW', 'CMPWI',
]

# floating point compare instructions
PPC_GRP_FLOAT_CMP = [
    'FCMPO', 'FCMPU',
    # vector compare
    'VCMPEQUB', 'VCMPEQUW', 'VCMPGTSH', 'VCMPGTSW', 'VCMPGTUB', 'VCMPGTUW',
]

# shift operation
PPC_GRP_SHIFT = [
    'ROTLW',
    'ROTLWI',
    'ROTLD',
    'ROTLDI',
    'SLBIA', 'SLBIE', 'SLBMFEE', 'SLBMTE', 'SLD', 'SLDI', 'SLW', 'SLWI',
    'SRAD', 'SRADI', 'SRAW', 'SRAWI', 'SRD', 'SRW', 'SRWI',
    'RLDCL', 'RLDCR', 'RLDIC', 'RLDICL', 'RLDICR',
    'RLDIMI', 'RLWIMI', 'RLWINM', 'RLWNM',
    # vector shift left
    'VSLB', 'VSLDOI', 'VSLH', 'VSLW',
    # vector splat
    'VSPLTB', 'VSPLTH', 'VSPLTISB', 'VSPLTISH', 'VSPLTISW', 'VSPLTW',
    # vector shift right
    'VSRAW', 'VSRB', 'VSRH', 'VSRW',
    # vector rotate
    'VRLW',
]

# Logical Instructions:
PPC_GRP_LOGIC = [
    'NOT',
    'AND', 'ANDC', 'ANDI', 'ANDIS',
    'CRAND', 'CRANDC', 'CRNAND', 'CRNOR', 'CROR', 'CRORC', 'CRXOR',
    'EVAND', 'EVANDC', 'EVNAND', 'EVNOR', 'EVOR', 'EVORC', 'EVXOR',
    'NAND', 'NOR',
    'OR', 'ORC', 'ORI', 'ORIS',
    'QVFAND', 'QVFANDC', 'QVFNAND', 'QVFNOR', 'QVFOR', 'QVFORC', 'QVFXOR',
    'VAND', 'VANDC', 'VNAND', 'VNOR', 'VOR', 'VORC', 'VXOR',
    'XOR', 'XORI', 'XORIS',
    'XXLAND', 'XXLANDC', 'XXLNAND', 'XXLNOR', 'XXLOR', 'XXLORC', 'XXLXOR',
]

# bit and byte instructions:
PPC_GRP_BIT = [
    # condition register clear
    'CRCLR',
    # count leading zeros
    'CNTLZD',
    'CNTLZW',
    # clear high-order bits register
    'CLRLDI',
    'CLRLWI',
    # extend sign
    'EXTSB',
    'EXTSW',
    'EXTSH',
]

PPC_GRP_MISC = [
    'NOP',
]

# control transfer instructions:
PPC_GRP_CTRANSFER = [
    'B', 'BL', 'BCTRL', 'BCTR', 'BLA', 'BLR', 'BLRL', 'BA',
    'SC',
    # trap
    'TRAP',
    'TW', 'TWEQ', 'TWEQI', 'TWGT', 'TWGTI', 'TWI', 'TWLGT', 'TWLGTI',
    'TWLLT', 'TWLLTI', 'TWLT', 'TWLTI', 'TWNE', 'TWNEI', 'TWU', 'TWUI',
]

PPC_GRP_COND_CTRANSFER = [
    'BC', 'BCA', 'BCCTR', 'BCCTRL', 'BCL', 'BCLA', 'BCLR', 'BCLRL', 'BCT',
    'BDNZ', 'BDNZA', 'BDNZF', 'BDNZFA', 'BDNZFL', 'BDNZFLA', 'BDNZFLRL',
    'BDNZL', 'BDNZLA', 'BDNZLR', 'BDNZLRL', 'BDNZT', 'BDNZTA', 'BDNZTL',
    'BDNZTLA', 'BDNZTLR', 'BDNZTLRL',
    'BDZ', 'BDZA', 'BDZF', 'BDZFA', 'BDZFL', 'BDZFLA', 'BDZFLR', 'BDZFLRL',
    'BDZL', 'BDZLA', 'BDZLR', 'BDZLRL', 'BDZT', 'BDZTA', 'BDZTL', 'BDZTLA',
    'BDZTLR', 'BDZTLRL',
    'BF', 'BFA', 'BFCTR', 'BFCTRL', 'BFL', 'BFLA', 'BFLR', 'BFLRL', 'BRINC',
    'BT', 'BTA', 'BTCTR', 'BTCTRL', 'BTL', 'BTLA', 'BTLR', 'BTLRL',
]

PPC_GRP_MAP = {
    9: PPC_GRP_FLOAT_DTRANSFER + PPC_GRP_FLOAT_CMP + PPC_GRP_FLOAT_ARITH,
    10: PPC_GRP_MISC + PPC_GRP_FLOAT_DTRANSFER + PPC_GRP_DTRANSFER,
    11: PPC_GRP_FLOAT_ARITH + PPC_GRP_SHIFT + PPC_GRP_ARITH,
    12: PPC_GRP_LOGIC,
    13: PPC_GRP_COND_CTRANSFER + PPC_GRP_CTRANSFER,
    20: PPC_GRP_FLOAT_DTRANSFER + PPC_GRP_DTRANSFER,
    21: PPC_GRP_FLOAT_ARITH + PPC_GRP_ARITH,
    22: PPC_GRP_FLOAT_CMP + PPC_GRP_CMP,
    23: PPC_GRP_SHIFT,
    24: PPC_GRP_BIT,
    26: PPC_GRP_COND_CTRANSFER,
    27: PPC_GRP_CTRANSFER,
    28: PPC_GRP_MISC,
    30: [],
}

