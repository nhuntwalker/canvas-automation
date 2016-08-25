"""Standardized tests for Doubly-Linked List data structure."""

import random
import string
import pytest
from itertools import product, chain
from collections import namedtuple

REQ_METHODS = [
    'push',
    'pop',
    'shift',
    'append',
    'remove',
]

MyDLLFixture = namedtuple(
    'MyDLLFixture', (
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


POP = list(range(3))
SHIFT = list(range(3))
REMOVE = list(range(3))
TEST_CASES = product(TEST_CASES, POP, SHIFT)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_dll(request):
    """Return a new empty instance of MyQueue."""
    from double import DList
    sequence, pop, shift = request.param

    instance = DList()
    for val in sequence:
        instance.append(val)

    # Also construct by appending or combination of the two

    if pop and sequence:
        for _ in range(min(len(sequence), pop)):
            instance.pop()
            sequence = sequence[1:]

    if shift and sequence:
        for _ in range(min(len(sequence), shift)):
            instance.shift()
            sequence = sequence[:-1]

    if sequence:
        first = sequence[0]
        last = sequence[-1]
        pop_error = None

        remove_idx = random.randrange(len(sequence))
        remove_val = sequence[remove_idx]
        sequence_after_remove = sequence[:remove_idx] + sequence[remove_idx + 1:]
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
    return MyDLLFixture(
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
def test_has_method(method, new_dll):
    """Test that queue has all the correct methods."""
    assert hasattr(new_dll.instance, method)


def test_push_pop(new_dll):
    """Test that unique pushed item is popped."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEPUSHPOPVALUE').hexdigest()
    new_dll.instance.push(val)
    assert new_dll.instance.pop() == val


def test_append_shift(new_dll):
    """Test that unique appended item is popped after all other items."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEAPPENDSHIFTVALUE').hexdigest()
    new_dll.instance.append(val)
    assert new_dll.instance.shift() == val


def test_push_shift(new_dll):
    """Test that unique pushed item is shifted after all other items."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEPUSHSHIFTVALUE').hexdigest()
    new_dll.instance.push(val)
    for _ in new_dll.sequence:
        new_dll.instance.shift()
    assert new_dll.instance.shift() == val


def test_append_pop(new_dll):
    """Test that unique appended item is popped after all other items."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEAPPENDPOPVALUE').hexdigest()
    new_dll.instance.append(val)
    for _ in new_dll.sequence:
        new_dll.instance.pop()
    assert new_dll.instance.pop() == val


def test_pop(new_dll):
    """Test that first value puted into queue is returned by pop."""
    if new_dll.pop_error is not None:
        pytest.skip()
    assert new_dll.instance.pop() == new_dll.first


def test_shift(new_dll):
    """Test that last value appended into queue is returned by shift."""
    if new_dll.pop_error is not None:
        pytest.skip()
    assert new_dll.instance.shift() == new_dll.last


def test_pop_error(new_dll):
    """Test that pop raises an error when expected."""
    if new_dll.pop_error is None:
        pytest.skip()
    with pytest.raises(new_dll.pop_error):
        new_dll.instance.pop()


def test_shift_error(new_dll):
    """Test that shift raises an error when expected."""
    if new_dll.pop_error is None:
        pytest.skip()
    with pytest.raises(new_dll.pop_error):
        new_dll.instance.shift()


def test_pop_sequence(new_dll):
    """Test that entire sequence is returned by successive pops."""
    sequence = list(new_dll.sequence)
    output = [new_dll.instance.pop() for _ in sequence]
    assert sequence == output


def test_shift_sequence(new_dll):
    """Test that entire sequence is returned by successive shifts."""
    sequence = list(reversed(new_dll.sequence))
    output = [new_dll.instance.shift() for _ in sequence]
    assert sequence == output


def test_remove_valid(new_dll):
    """Test that first item can be removed safely."""
    if new_dll.remove_val is None:
        pytest.skip()
    new_dll.instance.remove(new_dll.remove_val)
    result = list(new_dll.sequence_after_remove)
    output = [new_dll.instance.pop() for _ in result]
    assert output == result


def test_remove_error(new_dll):
    """Test remove throws ValueError when asked to remove a value not in DLL."""
    from hashlib import md5
    val = md5(b'SUPERUNIQUEREMOVEVALUE').hexdigest()
    with pytest.raises(new_dll.remove_error):
        new_dll.instance.remove(val)
