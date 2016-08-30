"""Standardized tests for Stack data structure."""

from __future__ import unicode_literals

import random
import string
import pytest
from hashlib import md5
from itertools import product, chain, permutations
from collections import namedtuple

REQ_METHODS = [
    'nodes',
    'edges',
    'add_node',
    'add_edge',
    'del_node',
    'del_edge',
    'has_node',
    'neighbors',
    'adjacent',
]

MyGraphFixture = namedtuple(
    'MyGraphFixture',
    ('instance', 'dict_', 'nodes', 'edges')
)


def _make_node_edge_combos(nodes):
    """Generate different combinations of edges for the given nodes."""
    nodes = set(nodes)
    all_possible = set(permutations(nodes, 2))
    max_edges = len(all_possible)

    yield nodes, set()  # No edges
    if all_possible:
        yield nodes, all_possible  # All possible edges
        for _ in range(min(max_edges, 10)):
            edge_count = random.randrange(1, max_edges)
            edges = random.sample(all_possible, edge_count)
            yield nodes, set(edges)


def _make_graph_dict(nodes, edges):
    """Make a dict representing the graph."""
    dict_ = {}
    for node in nodes:
        dict_[node] = set(edge[1] for edge in edges if edge[0] == node)
    return dict_


EDGE_CASES = [
    (),
    (0,),
    (0, 1),
    (1, 0),
    '',
    'a',
    'ab',
    'ba',
]

# lists of ints
INT_TEST_CASES = (random.sample(range(1000),
                  random.randrange(2, 20)) for n in range(10))

# strings
STR_TEST_CASES = (random.sample(string.printable,
                  random.randrange(2, 20)) for n in range(10))

TEST_CASES = chain(EDGE_CASES, INT_TEST_CASES, STR_TEST_CASES)

TEST_CASES = chain(*(_make_node_edge_combos(nodes) for nodes in TEST_CASES))


# POP = (True, False)

# TEST_CASES = product(TEST_CASES, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_graph(request):
    """Return a new empty instance of MyQueue."""
    from graph import Graph
    # nodes, edges = None, None
    nodes, edges = request.param
    dict_ = _make_graph_dict(nodes, edges)

    instance = Graph()
    for node in nodes:
        instance.add_node(node)

    for edge in edges:
        instance.add_edge(*edge)

    return MyGraphFixture(instance, dict_, nodes, edges)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that graph has all the correct methods."""
    from graph import Graph
    assert hasattr(Graph(), method)


def test_nodes_unique(new_graph):
    """Test that all graph's nodes are unique."""
    nodes = new_graph.instance.nodes()
    assert len(nodes) == len(set(nodes))


def test_nodes(new_graph):
    """Test that graph has all the inserted nodes."""
    assert set(new_graph.instance.nodes()) == new_graph.nodes


def test_has_node(new_graph):
    """Test that graph has all the inserted nodes."""
    assert all([new_graph.instance.has_node(n) for n in new_graph.nodes])


def test_edges(new_graph):
    """Test that graph has all the correct edges."""
    assert set(new_graph.instance.edges()) == new_graph.edges


# def test_neighbors_error(new_graph):
#     """Test that neighbors raises an error when given node is not in graph."""
#     val = 'nodenotingraph'
#     with pytest.raises(ValueError):
#         new_graph.instance.neighbors(val)


def test_del_node_error(new_graph):
    """Test that del_node raises an error when node is not in graph."""
    val = 'nodenotingraphtodelete'
    with pytest.raises(ValueError):
        new_graph.instance.del_node(val)


def test_add_new_node_no_neighbors(new_graph):
    """Test new node added without edges is in the graph without neighbors."""
    val = 'newnodenoneighbors'
    new_graph.instance.add_node(val)
    assert not set(new_graph.instance.neighbors(val))


def test_add_new_node_no_edges(new_graph):
    """Test new node added without edges is not neighbor of any other node."""
    val = 'newnodenoedges'
    new_graph.instance.add_node(val)
    other_neighbors = chain(*(new_graph.instance.neighbors(n)
                              for n in new_graph.instance.nodes()))
    assert val not in set(other_neighbors)


def test_add_new_edge_not_already_there(new_graph):
    """Check new nodes are added by add_edge when not already in graph."""
    new_nodes = {'notingraph1', 'notingraph3'}
    assert not new_nodes.issubset(new_graph.instance.nodes())
    new_graph.instance.add_edge(*new_nodes)
    assert new_nodes.issubset(new_graph.instance.nodes())

