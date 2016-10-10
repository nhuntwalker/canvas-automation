"""Test that sorting algorithms conform to expected sort result."""
from __future__ import unicode_literals
import pytest
import random
from cases import TEST_CASES
from importlib import import_module


IN_PLACE = True
STABLE = True
MODULENAME = 'insertion_sort'
FUNCNAME = 'insertion_sort'


module = import_module(MODULENAME)
funcdef = getattr(module, FUNCNAME)


# Need to add div and modulo capability
class AnonComparable(object):
    """Anonymous but unique comparable object."""

    def __init__(self, value):
        """Initialize with other value."""
        self.value = value

    def __ne__(self, other):
        """Non-equality."""
        return self.value != other.value

    def __lt__(self, other):
        """Less than."""
        return self.value < other.value

    def __gt__(self, other):
        """Greater than."""
        return self.value > other.value

    def __le__(self, other):
        """Less than or equal."""
        return self.value <= other.value

    def __ge__(self, other):
        """Greater than or equal."""
        return self.value >= other.value

    def __div__(self, other):
        """Division."""
        try:
            return self.value / other.value
        except AttributeError:
            return self.value / other

    def __floordiv__(self, other):
        """Floored division."""
        try:
            return self.value // other.value
        except AttributeError:
            return self.value / other

    def __mod__(self, other):
        """Modulo."""
        try:
            return self.value % other.value
        except AttributeError:
            return self.value / other


def _make_anon_list(size):
    """Return a list size items long of AnonComparable objects with dupes."""
    seq = []
    for n in range(size):
        if n % 2:
            seq.append(random.choice(seq))
        else:
            seq.append(AnonComparable(random.randrange(1000)))
    random.shuffle(seq)
    return seq


ANON_CASES = (_make_anon_list(size) for size in random.sample(range(1000), 100))


@pytest.mark.parametrize('sequence', TEST_CASES)
def test_sort(sequence):
    """Test that submitted sorting algo produces same result as builtin."""
    sequence = list(sequence)
    if IN_PLACE:
        funcdef(sequence)
        assert sequence == sorted(sequence)
    else:
        assert funcdef(sequence) == sorted(sequence)


@pytest.mark.parametrize('sequence', ANON_CASES)
def test_sort_anon(sequence):
    """Test that submitted sorting algo produces same result as builtin."""
    if not STABLE:
        pytest.skip()
    sequence = list(sequence)
    if IN_PLACE:
        funcdef(sequence)
        assert sequence == sorted(sequence)
    else:
        assert funcdef(sequence) == sorted(sequence)
