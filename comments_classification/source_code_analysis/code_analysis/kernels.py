"""
Author: Valerio Maggio (@leriomaggio)
Mail: valeriomaggio@gmail.com
"""

from itertools import ifilter, product
from functools import wraps
from math import sqrt
from numpy import sum as np_sum

# --------------------------------------------------------------------------
# Node Similarities (Kernels on Nodes)
# --------------------------------------------------------------------------

def match(n1, n2):
    """ Matching Function: determines wether two nodes are comparable. """
    return n1.instruction_class == n2.instruction_class

def features_similarity(n1, n2):
    """
        Feature Similarity: Computes a similarity value according to nodes attributes.
    """

    if n1.is_leaf_node and n2.is_leaf_node:
        return int(n1.instruction == n2.instruction and n1.label == n2.label)

    return int(n1.instruction == n2.instruction)


def structural_similarity(n1, n2):
    """
        Structural Similarity function (used to detect (without errors) up to Type 2 clones)
    """
    if n1.instruction == n2.instruction:
        return 1.0
    return 0.0

#------------------------------------------------------------------------------
# 01. Iterative Contiguous Kernel (Partial Trees)
#------------------------------------------------------------------------------

# Supporting functions

def compute_pairs_similarities(node_pairs_list, similarity=features_similarity):
    """
        Reminder: Improve using numpy.sum
    """
    return np_sum([similarity(n1, n2) for n1, n2 in node_pairs_list])


def extract_contiguous_kernel_nodes(t1, t2):
    """
        Extract all the possibile pairs of nodes that match

        --- (Improved version using itertools - TO BE TESTED.) ---

        Note that ifilter returns a Generator, rather than a list (this should me more
        efficient in terms of memory consumption).
        Nevertheless, the list could be trivially returned instead by removing
        the "i" from `ifilter` :-)
        (This will call the built-in Python `filter` function)

    """
    # return [(n1, n2) for n1 in t1.children for n2 in t2.children if match(n1, n2)]
    return ifilter(lambda p: match(p[0], p[1]), product(t1.children, t2.children))


# Memoization in Python with wraps - useful for normalization to avoid repeating calculations
# The memoization is exploited only in case of t1 == t2, i.e., we are computing
# normalization values.
# This is to avoid repeating useless calculations, while not wasting memory storing the
# computation of each pair.

def memo(func):
    cache = {}
    @wraps(func)
    def wrap(t1, t2, node_sim_func):
        if t1 == t2:
            if t1 not in cache:
                cache[t1] = func(t1, t2, node_sim_func)
            return cache[t1]
        return func(t1, t2, node_sim_func)
    return wrap

def iterative_kernel_function(node_pairs_list, node_similarity=features_similarity):
    """
        Iterative Tree Kernel Function
    """

    if not node_pairs_list or not len(node_pairs_list):
        return 0.0

    k = 0.0
    while len(node_pairs_list):
        pair = node_pairs_list.pop(0)
        k += compute_pairs_similarities([pair], similarity=node_similarity)
        matching_subtrees = extract_contiguous_kernel_nodes(pair[0], pair[1])
        node_pairs_list.extend(matching_subtrees)
    return k

@memo
def iterative_tree_kernel(tree1, tree2, node_similarity=features_similarity):
    '''
        Iterative Tree Kernel
    '''
    if not match(tree1, tree2):
        return 0.0
    return iterative_kernel_function([(tree1, tree2)], node_similarity)


# --------------------------------------------------------------------------
# Normalized Tree Kernel function
# --------------------------------------------------------------------------

def contiguous_tree_kernel(t1, t2, node_similarity=features_similarity):
    """
        Compute the Normalized version of the Contiguous Tree Kernel function
        (Value that range from 0 to 1)
    """

    kernel_sim = iterative_tree_kernel(t1, t2, node_similarity)

    #Normalization
    return float(kernel_sim) / sqrt(iterative_tree_kernel(t1, t1, node_similarity) *
                                    iterative_tree_kernel(t2, t2, node_similarity))