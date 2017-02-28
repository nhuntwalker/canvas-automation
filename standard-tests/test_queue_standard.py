"""Standardized tests for Queue data structure."""

import pytest
from importlib import import_module
from itertools import product
from collections import namedtuple
from cases import TEST_CASES, make_unique_value

MODULENAME = 'queue'
CLASSNAME = 'Queue'
DQ_ERROR = IndexError

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)

REQ_METHODS = [
    'enqueue',
    'dequeue',
    'peek',
    'size',
]

QueueFixture = namedtuple(
    'QueueFixture',
    ('instance', 'first', 'last', 'sequence', 'dq_error', 'size')
)


DQ = list(range(3))
PEEK = (True, False)

TEST_CASES = product(TEST_CASES, DQ, PEEK)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_queue(request):
    """Return a new empty instance of MyQueue."""
    sequence, dq, peek = request.param

    instance = ClassDef()
    for val in sequence:
        instance.enqueue(val)

    if peek:
        instance.peek()

    if dq and sequence:
        for _ in range(min(len(sequence), dq)):
            instance.dequeue()
            sequence = sequence[1:]
            if peek:
                instance.peek()

    if sequence:
        first = sequence[0]
        last = sequence[-1]
        dq_error = None

    else:
        first = None
        last = None
        dq_error = IndexError

    size = len(sequence)
    return QueueFixture(instance, first, last, sequence, dq_error, size)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that queue has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_enqueue(new_queue):
    """Test that unique enqueued item is dequeued after all other items."""
    val = make_unique_value()
    new_queue.instance.enqueue(val)
    for _ in range(new_queue.size):
        new_queue.instance.dequeue()
    assert new_queue.instance.dequeue() == val


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
    sequence = list(new_queue.sequence)
    output = [new_queue.instance.dequeue() for _ in sequence]
    assert sequence == output


def test_peek(new_queue):
    """Test that Queue.peek() returns the expected first value."""
    assert new_queue.instance.peek() == new_queue.first


def test_size(new_queue):
    """Test that Queue.size() returns the expected item count."""
    assert new_queue.instance.size() == new_queue.size
