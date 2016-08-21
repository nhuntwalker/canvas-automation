"""Standardized tests for Queue data structure."""

import random
import string
import pytest
from itertools import product, chain
from collections import namedtuple

REQ_METHODS = [
    'enqueue',
    'dequeue',
    'peek',
    'size',
]

MyQueueFixture = namedtuple(
    'MyQueueFixture',
    ('instance', 'first', 'last', 'sequence', 'dq_error', 'size')
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


DQ = (True, False)
PEEK = (True, False)

TEST_CASES = product(TEST_CASES, DQ, PEEK)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_queue(request):
    """Return a new empty instance of MyQueue."""
    from queue import Queue
    sequence, dq, peek = request.param

    instance = Queue()
    for val in sequence:
        instance.enqueue(val)

    if peek:
        instance.peek()

    if dq and sequence:
        instance.dequeue()
        sequence = sequence[1:]
    # Test instances that have been dequeued, then enqueued something else

    if sequence:
        first = sequence[0]
        last = sequence[-1]
        dq_error = None

    else:
        first = None
        last = None
        dq_error = IndexError

    size = len(sequence)
    return MyQueueFixture(instance, first, last, sequence, dq_error, size)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method, new_queue):
    """Test that queue has all the correct methods."""
    assert hasattr(new_queue.instance, method)


def test_dequeue(new_queue):
    """Test that first value puted into queue is returned by dequeue."""
    if new_queue.dq_error is not None:
        pytest.skip()
    assert new_queue.instance.dequeue() == new_queue.first


def test_dequeue_error(new_queue):
    """Test that dequeue raises an error when expected."""
    if new_queue.dq_error is None:
        pytest.skip()
    with pytest.raises(new_queue.dq_error):
        new_queue.instance.dequeue()


def test_dequeue_sequence(new_queue):
    """Test that entire sequence is returned by successive dequeues."""
    for item in new_queue.sequence:
        assert new_queue.instance.dequeue() == item


def test_peek(new_queue):
    """Test that Queue.peek() returns the expected first value."""
    assert new_queue.instance.peek() == new_queue.first


def test_size(new_queue):
    """Test that Queue.size() returns the expected item count."""
    assert new_queue.instance.size() == new_queue.size
