"""Standardized tests for the Heap data structure."""

import pytest
from itertools import product, chain
from collections import namedtuple
from importlib import import_module
from cases import (
    INT_EDGE_CASES,
    INT_TEST_CASES,
    MAX_INT,
    MIN_INT,
    make_unique_value,
)


MODULENAME = 'heap'
CLASSNAME = 'Heap'
# Min heap or max heap. defaults to minheap i.e. MAX == True
MAX = False

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)

REQ_METHODS = [
    'push',
    'pop',
]

HeapFixture = namedtuple(
    'HeapFixture',
    ('instance', 'pop_value', 'sorted_sequence', 'pop_error')
)

TEST_CASES = chain(INT_EDGE_CASES, INT_TEST_CASES)

INIT = (True, False)
POP = list(range(3))

TEST_CASES = product(TEST_CASES, INIT, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_heap(request):
    """Return a new empty instance of MyQueue."""
    sequence, init, pop = request.param
    # So that cases which are generators can be used more than once
    sequence = list(sequence)

    if init:
        instance = ClassDef(sequence)
    else:
        instance = ClassDef()
        for val in sequence:
            instance.push(val)

    sorted_sequence = sorted(sequence, reverse=MAX)
    if pop and sorted_sequence:
        for _ in range(min(len(sorted_sequence), pop)):
            instance.pop()
            sorted_sequence = sorted_sequence[1:]

    if sorted_sequence:
        pop_value = sorted_sequence[0]
        pop_error = None

    else:
        pop_value = None
        pop_error = IndexError

    return HeapFixture(instance, pop_value, sorted_sequence, pop_error)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that heap has all the correct methods."""
    assert hasattr(ClassDef(), method)


@pytest.mark.parametrize('val', [1, False, True, Exception])
def test_init_error(val):
    """Test that heap throws value error when initialized with non iterable."""
    with pytest.raises(TypeError):
        ClassDef(val)


def test_push_pop(new_heap):
    """Test that unique pushed item is popped before all other items."""
    val = MAX_INT if MAX else MIN_INT
    new_heap.instance.push(val)
    assert new_heap.instance.pop() == val


def test_pop(new_heap):
    """Test that max or min value (depending on spec) is returned by pop."""
    if new_heap.pop_value is None:
        pytest.skip()
    assert new_heap.instance.pop() == new_heap.pop_value


def test_pop_unchanged(new_heap):
    """Test pop value is unchanged after pushing a lesser/ greater value."""
    if new_heap.pop_value is None:
        pytest.skip()
    val = new_heap.pop_value + (-2 * MAX + 1)
    new_heap.instance.push(val)
    assert new_heap.instance.pop() == new_heap.pop_value


def test_pop_error(new_heap):
    """Test that pop raises an error when the heap is empty."""
    if new_heap.pop_error is None:
        pytest.skip()
    with pytest.raises(new_heap.pop_error):
        new_heap.instance.pop()


def test_pop_sequence(new_heap):
    """Test that entire heap is returned in sorted order by successive pops."""
    sequence = list(new_heap.sorted_sequence)
    output = [new_heap.instance.pop() for _ in sequence]
    assert sequence == output
