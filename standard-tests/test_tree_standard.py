"""Standardized tests for Binary Search Tree data structure."""
from __future__ import unicode_literals

import pytest
from importlib import import_module
from collections import namedtuple

from cases import TEST_CASES

MODULENAME = 'bst'
CLASSNAME = 'BinaryTree'
VAL_ATTR = 'value'
LEFT_ATTR = 'left_child'
RIGHT_ATTR = 'right_child'

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
        'sequence',
        'size',
        'depth',
        'balance',
    )
)


def _tree_checker(tree):
    """"Help function to check binary tree correctness."""
    this_val = getattr(tree, VAL_ATTR)
    left = getattr(tree, LEFT_ATTR)
    right = getattr(tree, RIGHT_ATTR)
    left_val = getattr(left, VAL_ATTR)
    right_val = getattr(right, VAL_ATTR)

    if tree is None or this_val is None:
        return True
    if right is not None and right_val < this_val:
        return False
    if left is not None and left_val > this_val:
        return False

    return all([_tree_checker(left), _tree_checker(right)])


def _unbalanced_depth(sequence):
    """Get the depth and balance from a random sequence."""
    if len(sequence) < 2:
        return len(sequence)
    current = sequence[0]
    less = [i for i in sequence if i < current]
    more = [i for i in sequence if i > current]
    return max(_unbalanced_depth(less), _unbalanced_depth(more)) + 1


def _unbalanced_balance(sequence):
    """Get the depth and balance from a random sequence."""
    try:
        root = sequence[0]
    except IndexError:
        return 0
    left = [i for i in sequence if i < root]
    right = [i for i in sequence if i > root]
    return _unbalanced_depth(left) - _unbalanced_depth(right)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_tree(request):
    """Return a new empty instance of MyQueue."""
    instance = ClassDef()
    sequence = request.param
    size = len(sequence)

    for item in sequence:
        instance.insert(item)

    depth = _unbalanced_depth(sequence)
    balance = _unbalanced_balance(sequence)

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
    assert all((new_tree.instance.contains(i) for i in new_tree.sequence))


def test_size(new_tree):
    """Test that size method returns the expected size."""
    assert new_tree.instance.size() == new_tree.size


def test_depth(new_tree):
    """Test that depth method returns expected depth."""
    assert new_tree.instance.depth() == new_tree.depth


def test_balance(new_tree):
    """Test that balance method returns expected balance."""
    assert new_tree.instance.balance() == new_tree.balance
