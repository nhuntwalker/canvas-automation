"""Standardized tests for Priority Queue data structure."""

import random
import pytest
from importlib import import_module
from operator import itemgetter
from collections import namedtuple
from itertools import product, repeat, cycle
from cases import (
    TEST_CASES,
    MAX_INT,
    MIN_INT,
    make_unique_value,
)


MODULENAME = 'priority_queue'
CLASSNAME = 'PriorityQueue'
# Highest priority when MAX=True
# Lowest priority first when MAX=False
MAX = True

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)

REQ_METHODS = [
    'insert',
    'pop',
    'peek',
]

PQueueFixture = namedtuple(
    'PQueueFixture',
    ('instance', 'first', 'last', 'sorted_sequence', 'pop_error')
)

# Give a priority to all test cases
# cases: priorities are all different
# priorities are all the same
# mix of some same, some different

# case where all vals are unique has vals


PRIORITIES = [
    repeat(0),  # all the same priority
    cycle((0, 1)),  # equal mix of two priorities
    random.sample(range(-10000, 10000), 100),  # 100 unique priorities
    (random.randrange(10) for _ in range(100))  # 100 random mix of ints 0-9
]

# iters of tuples for every combination of priority and input sequence
TEST_CASES = (zip(t, p) for t, p in product(TEST_CASES, PRIORITIES))

POP = list(range(3))
PEEK = (True, False)

TEST_CASES = product(TEST_CASES, POP, PEEK)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_priorityq(request):
    """Return a new empty instance of PQueueFixture."""
    sequence, pop, peek = request.param
    sequence = list(sequence)

    # sort sequence by second item
    sorted_sequence = sorted(sequence, key=itemgetter(1), reverse=MAX)

    instance = ClassDef()
    for tup in sequence:
        try:
            instance.insert(*tup)
        except TypeError:
            # Account for insert method accepting a tuple instead of 2 args
            instance.insert(tup)

    if peek:
        instance.peek()

    for _ in range(min(len(sorted_sequence), pop)):
        instance.pop()
        sorted_sequence = sorted_sequence[1:]
        if peek:
            instance.peek()

    try:
        first = sorted_sequence[0][0]
        last = sorted_sequence[-1][0]
        pop_error = None
    except IndexError:
        first = None
        last = None
        pop_error = IndexError

    return PQueueFixture(instance, first, last, sorted_sequence, pop_error)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that queue has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_pop(new_priorityq):
    """Test that first value puted into queue is returned by pop."""
    if new_priorityq.first is None:
        pytest.skip()
    assert new_priorityq.instance.pop() == new_priorityq.first


def test_insert_pop_top_priority(new_priorityq):
    """Test unique item inserted with top priority is immediately popped."""
    val = make_unique_value()
    priority = MAX_INT if MAX else MIN_INT
    new_priorityq.instance.insert(val, priority)
    assert new_priorityq.instance.pop() == val


def test_insert_pop_bottom_priority(new_priorityq):
    """Test unique item insertd with low priority is popped last."""
    val = make_unique_value()
    priority = MIN_INT if MAX else MAX_INT
    new_priorityq.instance.insert(val, priority)
    for _ in new_priorityq.sorted_sequence:
        new_priorityq.instance.pop()
    assert new_priorityq.instance.pop() == val


def test_pop_error(new_priorityq):
    """Test that pop raises an error when expected."""
    if new_priorityq.pop_error is None:
        pytest.skip()
    with pytest.raises(new_priorityq.pop_error):
        new_priorityq.instance.pop()


def test_pop_sequence(new_priorityq):
    """Test that entire sequence is returned by successive pops."""
    sequence = [item[0] for item in new_priorityq.sorted_sequence]
    output = [new_priorityq.instance.pop() for _ in sequence]
    assert sequence == output


def test_peek(new_priorityq):
    """Test that Queue.peek() returns the expected first value."""
    assert new_priorityq.instance.peek() == new_priorityq.first
