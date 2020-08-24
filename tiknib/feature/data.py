"""This module is for adding more features in the near future."""

from numpy import ones, nonzero, bool

from tiknib.utils import mean

from . import Feature


class DataFeature(Feature):
    @staticmethod
    def get(f):
        consts = f["consts"]
        strs = f["strings"]
        str_lens = list(map(lambda x: len(x[1]), strs))
        str_nums = list(map(lambda x: make_abstract_number(x[1]), strs))

        features = {}
        features["data_num_consts"] = len(consts)
        features["data_avg_consts"] = mean(consts)
        features["data_sum_consts_seq"] = sum(
            map(lambda x: (x[0] + 1) * x[1], enumerate(consts))
        )
        features["data_num_strings"] = len(strs)
        features["data_sum_strlen"] = sum(str_lens)
        features["data_avg_strlen"] = mean(str_lens)
        features["data_sum_strlen_seq"] = sum(
            map(lambda x: (x[0] + 1) * x[1], enumerate(str_lens))
        )
        features["data_sum_abs_strings"] = sum(str_nums)
        features["data_avg_abs_strings"] = mean(str_nums)
        features["data_sum_abs_strings_seq"] = sum(
            map(lambda x: (x[0] + 1) * x[1], enumerate(str_nums))
        )
        return features


def gen_primes(n):
    sieve = ones(n // 2, dtype=bool)
    for i in range(3, int(n ** 0.5) + 1, 2):
        if sieve[i // 2]:
            sieve[i * i // 2 :: i] = False
    return 2 * nonzero(sieve)[0][1::] + 1


PRIME_MAX = 100000
PRIMES = gen_primes(PRIME_MAX)


def make_abstract_number(s):
    global PRIMES, PRIME_MAX
    if len(PRIMES) < len(s) - 1:
        PRIME_MAX *= 100
        PRIMES = gen_primes(PRIME_MAX)
        return make_number(s)
    return PRIMES[len(s) - 1].item(0)
