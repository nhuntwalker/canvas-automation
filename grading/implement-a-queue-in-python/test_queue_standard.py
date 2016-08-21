"""Examples for blog post about pytest parametrization."""

import random
import string
import pytest

from collections import namedtuple

MyQueueFixture = namedtuple(
    'MyQueueFixture',
    ('instance', 'first', 'sequence', 'pop_error', 'size')
)

EDGE_CASES = [
    (),
    (0,),
    (0, 1),
    (1, 0),
    (''),
    ('a'),
    ('ab'),
    ('ba'),
]

INT_TEST_CASES = [random.sample(range(1000),
                  random.randrange(2, 100)) for n in range(10)]


STR_TEST_CASES = [random.sample(string.printable,
                  random.randrange(2, 100)) for n in range(10)]

TEST_CASES = EDGE_CASES + INT_TEST_CASES + STR_TEST_CASES


@pytest.fixture(scope='function', params=TEST_CASES)
def queue(request):
    """Return a new empty instance of MyQueue."""
    from my_queue import MyQueue
    instance = MyQueue()
    sequence = request.param
    size = len(sequence)
    if sequence:
        first = sequence[0]
        pop_error = None
    else:
        first = None
        pop_error = IndexError
    for val in request.param:
        instance.put(val)
    return MyQueueFixture(instance, first, sequence, pop_error, size)


def test_queue_get(queue):
    """Test that first value puted into queue is returned by get."""
    assert queue.instance.get() == queue.first


def test_queue_get_sequence(queue):
    """Test that first value puted into queue is returned by get."""
    for item in queue.sequence:
        assert queue.instance.get() == item


def test_queue_size(queue):
    """Test that MyQueue.size() returns the expected item count."""
    assert queue.instance.size() == queue.size


# @pytest.fixture(scope='function', params=TEST_CASES)
# def queue(request):
#     """Return a new empty instance of MyQueue."""
#     from my_queue import MyQueue
#     instance = MyQueue()
#     for val in request.param:
#         instance.put(val)
#     return instance


# @pytest.fixture(scope='function')
# def queue():
#     """Return a new empty instance of MyQueue."""
#     from my_queue import MyQueue
#     instance = MyQueue()
#     return instance


# def test_queue_get(queue):
#     """Test that first value puted into queue is returned by get."""
#     queue.put(100)
#     assert queue.get() == 100


# def test_queue_get():
#     """Test that first value puted into queue is returned by get."""
#     from my_queue import MyQueue
#     queue = MyQueue()
#     queue.put(100)
#     assert queue.get() == 100


# def test_queue_get2():
#     """Test that first value puted into queue is returned by get."""
#     from my_queue import MyQueue
#     queue = MyQueue()
#     queue.put(1)
#     queue.put(2)
#     queue.put(3)
#     queue.put(4)
#     assert queue.get() == 1


# def test_queue_get3():
#     """Test that first value puted into queue is returned by get."""
#     from my_queue import MyQueue
#     queue = MyQueue()
#     queue.put('first')
#     queue.put('second')
#     queue.put('third')
#     queue.put('fourth')
#     assert queue.get() == 'first'
