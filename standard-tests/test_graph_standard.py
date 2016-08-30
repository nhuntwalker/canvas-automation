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
    ('instance', 'dict', 'nodes', 'edges')
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

# LIST_TEST_CASES
# SET_TEST_CASES
# DICT_TEST_CASES

TEST_CASES = chain(EDGE_CASES, INT_TEST_CASES, STR_TEST_CASES)


POP = (True, False)

TEST_CASES = product(TEST_CASES, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_graph(request):
    """Return a new empty instance of MyQueue."""
    from graph import Graph
    sequence, pop = request.param

    instance = Graph()
    for val in sequence:
        instance.push(val)

    if pop and sequence:
        instance.pop()
        sequence = sequence[:-1]

    if sequence:
        first = sequence[-1]
        last = sequence[0]
        pop_error = None

    else:
        first = None
        last = None
        pop_error = IndexError

    return MyGraphFixture(instance, first, last, sequence, pop_error)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that queue has all the correct methods."""
    from graph import Graph
    assert hasattr(Graph(), method)
