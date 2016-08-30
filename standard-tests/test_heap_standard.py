"""Standardized tests for the Heap data structure."""

# intialize by __init__
# initialize by pushing one at a time

import random
import pytest
from itertools import product, chain
from collections import namedtuple

REQ_METHODS = [
    'push',
    'pop',
]

MyHeapFixture = namedtuple(
    'MyStackFixture',
    ('instance', 'pop_value', 'sorted_sequence', 'pop_error')
)

EDGE_CASES = [
    (),
    (0,),
    (0, 1),
    (1, 0),
    range(3),
    range(2, -1, -1),
    range(100),
    range(99, -1, -1),
]

# lists of ints
INT_TEST_CASES = (random.sample(range(1000),
                  random.randrange(2, 40)) for n in range(10))

TEST_CASES = chain(EDGE_CASES, INT_TEST_CASES)

INIT = (True, False)
POP = list(range(3))

TEST_CASES = product(TEST_CASES, INIT, POP)

# Min heap or max heap. defaults to minheap i.e. MAX == True
MAX = False
LIMIT = 999999999999999999999999999


@pytest.fixture(scope='function', params=TEST_CASES)
def new_heap(request):
    """Return a new empty instance of MyQueue."""
    from binary_heap import BinaryHeap
    sequence, init, pop = request.param
    # So that cases which are generators can be used more than once
    sequence = list(sequence)

    if init:
        instance = BinaryHeap(sequence)
    else:
        instance = BinaryHeap()
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

    return MyHeapFixture(instance, pop_value, sorted_sequence, pop_error)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that heap has all the correct methods."""
    from bin_heap import BinHeap
    assert hasattr(BinHeap(), method)


@pytest.mark.parametrize('val', [1, False, True, None, Exception])
def test_init_error(val):
    """Test that heap throws value error when initialized with non iterable."""
    from binary_heap import BinaryHeap
    with pytest.raises(TypeError):
        BinaryHeap(val)


def test_push_pop(new_heap):
    """Test that unique pushed item is popped before all other items."""
    val = LIMIT if MAX else -LIMIT
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
