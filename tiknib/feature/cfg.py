"""This module is for adding more features in the near future."""

import networkx as nx
from functools import reduce

from tiknib.utils import mean

from . import Feature


class CfgFeature(Feature):
    @staticmethod
    def get(f):
        cfg = f["cfg"]
        if not cfg:
            return {}

        G = nx.DiGraph(cfg)
        start_node = min(list(G))
        loops, back_edges = natural_loops(G, start_node)
        loops_inter, _ = natural_loops(G, start_node, use_intersect=True)
        sccs = list(nx.strongly_connected_components(G))
        in_degrees = dict(G.in_degree())
        in_degree_val = list(in_degrees.values())
        out_degrees = dict(G.out_degree())
        out_degree_val = list(out_degrees.values())
        degrees = dict(G.degree())
        degree_val = list(degrees.values())
        bfs_tree = nx.bfs_tree(G, start_node)
        max_width, max_depth = get_widthdepth(bfs_tree, start_node)
        # Do not calculate cycles. O((n + e)(c + 1)) takes too much time.
        # cycles = list(nx.simple_cycles(G))

        features = {}
        features["cfg_size"] = f["cfg_size"]
        features["cfg_num_loops"] = len(loops)
        features["cfg_num_loops_inter"] = len(loops_inter)
        features["cfg_num_scc"] = len(sccs)
        features["cfg_num_backedges"] = len(back_edges)
        features["cfg_num_bfs_edges"] = len(bfs_tree.edges())
        features["cfg_max_width"] = max_width
        features["cfg_max_depth"] = max_depth
        features["cfg_sum_loopsize"] = sum(list(map(len, loops)))
        features["cfg_sum_loopintersize"] = sum(list(map(len, loops_inter)))
        features["cfg_sum_sccsize"] = sum(list(map(len, sccs)))
        features["cfg_avg_loopsize"] = mean(list(map(len, loops)))
        features["cfg_avg_loopintersize"] = mean(list(map(len, loops_inter)))
        features["cfg_avg_sccsize"] = mean(list(map(len, sccs)))
        features["cfg_num_indegree"] = sum(in_degree_val)
        features["cfg_num_outdegree"] = sum(out_degree_val)
        features["cfg_num_degree"] = sum(degree_val)
        features["cfg_avg_indegree"] = mean(list(in_degree_val))
        features["cfg_avg_outdegree"] = mean(list(out_degree_val))
        features["cfg_avg_degree"] = mean(list(degree_val))
        return features


# Below function is slightly different from immediate_dominators() in NetworkX,
# for fetching natural loops. Please check below url:
# https://networkx.github.io/documentation/stable/_modules/networkx/algorithms/dominance.html#immediate_dominators
def dominators(G, start):
    def _intersect(u, v):
        return u.intersection(v)

    if start not in G:
        raise nx.NetworkXError("start is not in G")

    dom = {start: {start}}
    order = list(nx.dfs_postorder_nodes(G, start))
    order.pop()
    for u in order:
        dom[u] = set(order)
    order.reverse()

    change = True
    while change:
        change = False
        for n in order:
            new_dom = set([n])
            new_dom = new_dom.union(
                reduce(_intersect, (dom[v] for v in G.pred[n] if v in dom))
            )
            if new_dom != dom[n]:
                dom[n] = new_dom
                change = True
    return dom


def natural_loops(G, start, use_intersect=False):
    def _union(u, v):
        return u.union(v)

    doms = dominators(G, start)
    back_edges = []
    # dst is the loop header
    for src, dst in G.edges():
        if src in doms and dst in doms[src]:
            back_edges.append((src, dst))

    loops = []
    heads = []
    # dst is the loop header
    for src, dst in back_edges:
        loop = set([src, dst])
        queue = set([src])
        while queue:
            t = queue.pop()
            for s, d in G.in_edges(t):
                if s != dst and s not in loop:
                    loop.add(s)
                    queue.add(s)
        loops.append(loop)
        heads.append(dst)
    assert len(loops) == len(heads)

    # merge intersection loops to one
    if use_intersect:
        new_loops = []
        new_heads = []
        min_list = []
        for idx, loop in enumerate(loops):
            updated = False
            for idx_check, loop_check in enumerate(new_loops):
                if heads[idx] == new_heads[idx_check]:
                    new_loops[idx_check] = _union(loop, loop_check)
                    updated = True
                    break
            if not updated:
                new_loops.append(loop)
                new_heads.append(heads[idx])
        loops = new_loops
    return loops, back_edges


def get_widthdepth(G, start):
    max_width = 0
    max_depth = 0
    Q = [start]
    while Q:
        parents = Q
        max_depth += 1
        max_width = max(max_width, len(parents))
        children = set()
        for parent in parents:
            for child in G[parent]:
                children.add(child)
        Q = children
    return max_width, max_depth
