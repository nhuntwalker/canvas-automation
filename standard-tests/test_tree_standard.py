"""Standardized tests for Binary Search Tree data structure."""
from __future__ import unicode_literals

import random
import pytest
from importlib import import_module
from itertools import permutations
from collections import namedtuple

from cases import TEST_CASES

MODULENAME = 'bst'
CLASSNAME = 'BinaryTree'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)


REQ_METHODS = [
    'insert',
    'contains',
    'size',
    'depth',
    'balance',
]

BinaryTreeFixture = namedtuple(
    'BinaryTreeFixture', (
        'instance',
        'sequence'
        'size',
        'depth',
        'balance',
    )
)


def _unbalanced_depth(sequence):
    """Get the depth and balance from a random sequence."""
    size = len(sequence)
    if size < 2:
        return size
    current = sequence[0]
    less = [i for i in sequence if i < current]
    more = [i for i in sequence if i > current]
    return max(_unbalanced_depth(less), _unbalanced_depth(more)) + 1


@pytest.fixture(scope='function', params=TEST_CASES)
def new_tree(request):
    """Return a new empty instance of MyQueue."""
    instance = ClassDef()
    sequence = request.param
    size = len(sequence)
    for item in sequence:
        instance.insert(item)

    depth = _unbalanced_depth(sequence)
    balance = 0

    return BinaryTreeFixture(
        instance,
        sequence,
        size,
        depth,
        balance,
    )


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_contains(new_tree):
    """Test that tree contains all items pushed into it."""
    for item in new_tree.sequence:
        assert new_tree.instance.contains(item)


def test_size(new_tree):
    """Test that size method returns the expected size."""
    assert new_tree.instance.size() == new_tree.size
