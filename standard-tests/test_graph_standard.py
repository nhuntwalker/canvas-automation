"""Standardized tests for Stack data structure."""

import random
import string
import pytest
from itertools import product, chain
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
                  random.randrange(2, 100)) for n in range(10))

# strings
STR_TEST_CASES = (random.sample(string.printable,
                  random.randrange(2, 100)) for n in range(10))

TEST_CASES = chain(EDGE_CASES, INT_TEST_CASES, STR_TEST_CASES)


POP = (True, False)

TEST_CASES = product(TEST_CASES, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_graph(request):
    """Return a new empty instance of MyQueue."""
    from graph import Graph
    nodes, pop = request.param

    instance = Graph()
    for val in nodes:
        instance.add_node(val)

    # if pop and nodes:
    #     instance.pop()
    #     nodes = nodes[:-1]

    if nodes:
        pop_error = None

    else:
        pop_error = IndexError

    return MyGraphFixture(instance, 'dict_', nodes, 'edges')


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
    assert set(new_graph.instance.nodes()) == set(new_graph.nodes)
