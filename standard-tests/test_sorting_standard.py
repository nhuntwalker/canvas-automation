"""Test that sorting algorithms conform to expected sort result."""
from __future__ import unicode_literals
import pytest
from cases import TEST_CASES
from importlib import import_module


MODULENAME = 'insertion_sort'
FUNCNAME = 'insertion_sort'


module = import_module(MODULENAME)
funcdef = getattr(module, FUNCNAME)


# Add tests for stability using anonymous but unique comparable objects


@pytest.mark.parametrize('sequence', TEST_CASES)
def test_sort(sequence):
    """Test that submitted sorting algo produces same result as builtin."""
    assert funcdef(sequence) == sorted(sequence)
