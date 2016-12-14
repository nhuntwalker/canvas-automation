"""Standardized tests for Singly Linked List."""

import pytest
from importlib import import_module
from itertools import product
from collections import namedtuple
import random
from cases import TEST_CASES

BALANCED = True
MODULENAME = 'linked_list'
CLASSNAME = 'LinkedList'
NODE_CLASSNAME = 'Node'
NODE_VAL_ATTR = 'val'
HEAD_ATTR = 'head'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)
Node = getattr(module, NODE_CLASSNAME)


REQ_METHODS = [
    'push',
    'pop',
    'size',
    'search',
    'remove',
    'display',
]

LinkedListFixture = namedtuple(
    'LinkedListFixture', (
        'instance',
        'first',
        'last',
        'sequence',
        'pop_error',
        'size',
        'search_val',
        'search_error',
        'remove_node',
        'display_result',
    )
)


POP = list(range(5))

TEST_CASES = product(TEST_CASES, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_ll(request):
    """Return a new empty instance of MyQueue."""
    sequence, pop = request.param
    instance = ClassDef()
    for val in sequence:
        instance.push(val)

    if pop and sequence:
        for _ in range(min(len(sequence), pop)):
            instance.pop()
            sequence = sequence[:-1]

    if sequence:
        first = sequence[0]
        last = sequence[-1]
        pop_error = None
        search_val = random.choice(sequence)
        search_error = None
        remove_node = instance.search(random.choice(sequence))

    else:
        first = None
        last = None
        pop_error = IndexError
        search_val = None
        search_error = ValueError
        remove_node = None

    size = len(sequence)
    display_result = str(tuple(reversed(sequence)))
    return LinkedListFixture(
        instance,
        first,
        last,
        sequence,
        pop_error,
        size,
        search_val,
        search_error,
        remove_node,
        display_result,
    )


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that queue has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_push(new_ll):
    """Test that unique pushed item is popped befire all other items."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEFLAGVALUE').hexdigest()
    new_ll.instance.push(val)
    assert new_ll.instance.pop() == val


def test_pop(new_ll):
    """Test that last value puted into linked list is returned by pop."""
    if new_ll.pop_error is not None:
        pytest.skip()
    assert new_ll.instance.pop() == new_ll.last


def test_pop_error(new_ll):
    """Test that pop raises an error when expected."""
    if new_ll.pop_error is None:
        pytest.skip()
    with pytest.raises(new_ll.pop_error):
        new_ll.instance.pop()


def test_pop_sequence(new_ll):
    """Test that entire sequence is returned by successive pops."""
    sequence = list(reversed(new_ll.sequence))
    output = [new_ll.instance.pop() for _ in sequence]
    assert sequence == output


def test_size(new_ll):
    """Test that LinkedList.size() returns the expected item count."""
    assert new_ll.instance.size() == new_ll.size


def test_search_node_type(new_ll):
    """Test that search returns an instance of the Node class."""
    if new_ll.search_val is None:
        pytest.skip()
    node = new_ll.instance.search(new_ll.search_val)
    assert isinstance(node, Node)


def test_search_node_val(new_ll):
    """Test that the node returned by search has the correct val attribute."""
    if new_ll.search_val is None:
        pytest.skip()
    node = new_ll.instance.search(new_ll.search_val)
    assert getattr(node, NODE_VAL_ATTR) == new_ll.search_val
