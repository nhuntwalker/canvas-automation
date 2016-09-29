"""Test that sorting algorithms conform to expected sort result."""
from __future__ import unicode_literals
import pytest
from cases import TEST_CASES
from importlib import import_module


IN_PLACE = True
MODULENAME = 'insertion_sort'
FUNCNAME = 'insertion_sort'


module = import_module(MODULENAME)
funcdef = getattr(module, FUNCNAME)


class AnonComparable(object):
    """Anonymous but unique comparable object."""

    def __init__(self, value):
        """Initialize with other value."""
        self.value = value

    def __eq__(self, other):
        """Equality."""
        return self.value == other.value

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
        return self.value == other.value


ANON_CASES = ((AnonComparable(val) for val in seq) for seq in TEST_CASES)


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
    sequence = list(sequence)
    if IN_PLACE:
        funcdef(sequence)
        assert sequence == sorted(sequence)
    else:
        assert funcdef(sequence) == sorted(sequence)
