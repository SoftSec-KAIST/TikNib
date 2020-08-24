"""This module is for adding more features in the near future."""

from . import Feature


class CgFeature(Feature):
    @staticmethod
    def get(f):
        callers = f["callers"]
        callees = f["callees"]
        imported_callees = f["imported_callees"]

        caller_names = set(map(lambda x: x[0], callers))
        callee_names = set(map(lambda x: x[0], callees))
        imported_callee_names = set(map(lambda x: x[0], imported_callees))

        features = {}
        features["cg_num_callers"] = len(caller_names)
        features["cg_num_callees"] = len(callee_names)
        features["cg_num_imported_callees"] = len(imported_callee_names)
        features["cg_num_incalls"] = len(callers)
        features["cg_num_outcalls"] = len(callees)
        features["cg_num_imported_calls"] = len(imported_callees)
        return features
