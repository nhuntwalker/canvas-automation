"""Standardized tests for Stack data structure."""

import random
import string
import pytest
from itertools import product, chain
from collections import namedtuple

REQ_METHODS = [
    'push',
    'pop',
]

StackFixture = namedtuple(
    'StackFixture',
    ('instance', 'first', 'last', 'sequence', 'pop_error')
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
def new_stack(request):
    """Return a namedtuple containing test information."""
    from stack import Stack
    sequence, pop = request.param

    instance = Stack()
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

    return StackFixture(instance, first, last, sequence, pop_error)


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that queue has all the correct methods."""
    from stack import Stack
    assert hasattr(Stack(), method)


def test_push(new_stack):
    """Test that unique pushed item is poped befire all other items."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEFLAGVALUE').hexdigest()
    new_stack.instance.push(val)
    assert new_stack.instance.pop() == val


def test_pop(new_stack):
    """Test that first value puted into queue is returned by pop."""
    if new_stack.pop_error is not None:
        pytest.skip()
    assert new_stack.instance.pop() == new_stack.first


def test_pop_error(new_stack):
    """Test that pop raises an error when expected."""
    if new_stack.pop_error is None:
        pytest.skip()
    with pytest.raises(new_stack.pop_error):
        new_stack.instance.pop()


def test_pop_sequence(new_stack):
    """Test that entire sequence is returned by successive pops."""
    sequence = list(reversed(new_stack.sequence))
    output = [new_stack.instance.pop() for _ in sequence]
    assert sequence == output
