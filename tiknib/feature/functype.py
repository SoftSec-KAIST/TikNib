"""This module is for adding more features in the near future."""

from functools import reduce

from tiknib.utils import mean

from . import Feature


class TypeFeature(Feature):
    @staticmethod
    def get(f):
        args = f["args"]
        arg_types = f["abstract_args_type"]
        ret_type = f["abstract_ret_type"]

        features = {}
        features["data_num_args"] = len(arg_types)
        if arg_types:
            type_nums = list(map(lambda x: make_number(x), arg_types))
            features["data_sum_arg_type"] = sum(type_nums)
            features["data_avg_arg_type"] = mean(type_nums)
            features["data_mul_arg_type"] = reduce(lambda x, y: x * y, type_nums)
            features["data_sum_arg_type_seq"] = sum(
                map(lambda x: (x[0] + 1) * x[1], enumerate(type_nums))
            )
        features["data_ret_type"] = make_number(ret_type)
        return features


TYPE_MAP = {
    "func": 2,
    "void *": 2,
    "struct *": 2,
    "short *": 2,
    "int *": 2,
    "char *": 2,
    "enum *": 2,
    "float *": 2,
    "func *": 2,
    "union *": 2,
    "int": 3,
    "char": 5,
    "short": 7,
    "enum": 11,
    "float": 13,
    "struct": 17,
    "union": 17,
    "void": 19,
}


def make_number(t):
    return TYPE_MAP[t]
