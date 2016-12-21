"""Standardized tests for Deque data structure."""

import random
import pytest
from itertools import product
from collections import namedtuple
from importlib import import_module
from cases import TEST_CASES, make_unique_value

MODULENAME = 'deque'
CLASSNAME = 'Deque'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)

REQ_METHODS = [
    'append',
    'appendleft',
    'pop',
    'popleft',
    'peek',
    'peekleft',
    'size',
]

DequeFixture = namedtuple(
    'DequeFixture', (
        'instance',
        'first',
        'last',
        'sequence',
        'size',
        'pop_error',
        'remove_val',
        'sequence_after_remove',
        'remove_error',
    )
)


POP = list(range(3))
POPLEFT = list(range(3))
REMOVE = list(range(3))  # implement removes in setup
TEST_CASES = product(TEST_CASES, POPLEFT, POP)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_deque(request):
    """Return a new empty instance of DequeFixture."""
    from deque import Deque
    sequence, popleft, pop = request.param
    sequence = list(sequence)

    instance = Deque()
    for val in sequence:
        instance.append(val)

    # Also construct by appending left or combination of the two

    if popleft and sequence:
        for _ in range(min(len(sequence), popleft)):
            instance.popleft()
            sequence = sequence[1:]

    if pop and sequence:
        for _ in range(min(len(sequence), pop)):
            instance.pop()
            sequence = sequence[:-1]

    if sequence:
        first = sequence[0]
        last = sequence[-1]
        pop_error = None

        sequence_after_remove = sequence[:]
        remove_val = random.choice(sequence)
        sequence_after_remove.remove(remove_val)
        # first, last, middle
        # multiple removes

    else:
        first = None
        last = None
        pop_error = IndexError
        remove_val = None
        sequence_after_remove = None

    size = len(sequence)
    remove_error = ValueError
    return DequeFixture(
        instance,
        first,
        last,
        sequence,
        size,
        pop_error,
        remove_val,
        sequence_after_remove,
        remove_error,
    )


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that queue has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_appendleft_popleft(new_deque):
    """Test that unique appendlefted item is popped."""
    val = make_unique_value()
    new_deque.instance.appendleft(val)
    assert new_deque.instance.popleft() == val


def test_append_pop(new_deque):
    """Test that unique appended item is popped after all other items."""
    val = make_unique_value()
    new_deque.instance.append(val)
    assert new_deque.instance.pop() == val


def test_appendleft_pop(new_deque):
    """Test that unique appendlefted item is poped after all other items."""
    val = make_unique_value()
    new_deque.instance.appendleft(val)
    for _ in new_deque.sequence:
        new_deque.instance.pop()
    assert new_deque.instance.pop() == val


def test_append_popleft(new_deque):
    """Test that unique appended item is popped after all other items."""
    val = make_unique_value()
    new_deque.instance.append(val)
    for _ in new_deque.sequence:
        new_deque.instance.popleft()
    assert new_deque.instance.popleft() == val


def test_popleft(new_deque):
    """Test that first value puted into queue is returned by pop."""
    if new_deque.pop_error is not None:
        pytest.skip()
    assert new_deque.instance.popleft() == new_deque.first


def test_pop(new_deque):
    """Test that last value appended into queue is returned by pop."""
    if new_deque.pop_error is not None:
        pytest.skip()
    assert new_deque.instance.pop() == new_deque.last


def test_popleft_error(new_deque):
    """Test that pop raises an error when expected."""
    if new_deque.pop_error is None:
        pytest.skip()
    with pytest.raises(new_deque.pop_error):
        new_deque.instance.popleft()


def test_pop_error(new_deque):
    """Test that pop raises an error when expected."""
    if new_deque.pop_error is None:
        pytest.skip()
    with pytest.raises(new_deque.pop_error):
        new_deque.instance.pop()


def test_popleft_sequence(new_deque):
    """Test that entire sequence is returned by successive pops."""
    sequence = list(new_deque.sequence)
    output = [new_deque.instance.popleft() for _ in sequence]
    assert sequence == output


def test_pop_sequence(new_deque):
    """Test that entire sequence is returned by successive pops."""
    sequence = list(reversed(new_deque.sequence))
    output = [new_deque.instance.pop() for _ in sequence]
    assert sequence == output


def test_peek(new_deque):
    """Test that Deque.peek() returns the expected first value."""
    assert new_deque.instance.peek() == new_deque.last


def test_peekleft(new_deque):
    """Test that Deque.peek() returns the expected first value."""
    assert new_deque.instance.peekleft() == new_deque.first


def test_size(new_deque):
    """Test that Queue.size() returns the expected item count."""
    assert new_deque.instance.size() == new_deque.size
