"""Standardized tests for Binary Search Tree data structure."""
from __future__ import unicode_literals

import pytest
from importlib import import_module
from collections import namedtuple

from cases import TEST_CASES, MIN_STR, MAX_STR, MIN_INT, MAX_INT


MODULENAME = 'bst'
CLASSNAME = 'BinaryTree'
ROOT_ATTR = 'root'
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
        'left_overbalance',
        'right_overbalance',
        'to_insert',
    )
)


def _tree_checker(tree):
    """"Help function to check binary tree correctness."""
    if tree is None:
        return True

    this_val = getattr(tree, VAL_ATTR)
    left = getattr(tree, LEFT_ATTR)
    right = getattr(tree, RIGHT_ATTR)

    if right is not None and getattr(right, VAL_ATTR) < this_val:
        return False
    if left is not None and getattr(left, VAL_ATTR) > this_val:
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


def _left_overbalance_str():
    """Generate string values to create long tail on the left side of tree."""
    for n in range(100, 0, -1):
        yield MIN_STR * n


def _right_overbalance_str():
    """Generate string values to create long tail on the left side of tree."""
    for n in range(1, 101):
        yield MAX_STR * n


_left_overbalance_int = range(MIN_INT, MIN_INT - 100, -1)
_right_overbalance_int = range(MAX_INT, MAX_INT + 100)


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

    if not sequence or isinstance(sequence[0], int):
        left_overbalance = _left_overbalance_int
        right_overbalance = _right_overbalance_int
        to_insert = MAX_INT
    elif isinstance(sequence[0], str):
        left_overbalance = _left_overbalance_str
        right_overbalance = _right_overbalance_str
        to_insert = 'superuniquestring'

    return BinaryTreeFixture(
        instance,
        sequence,
        size,
        depth,
        balance,
        left_overbalance,
        right_overbalance,
        to_insert,
    )


@pytest.mark.parametrize('method', REQ_METHODS)
def test_has_method(method):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method)


def test_invariant(new_tree):
    """Check tree against the tree invariant."""
    assert _tree_checker(getattr(new_tree.instance, ROOT_ATTR))


def test_invariant_after_insert(new_tree):
    """Check tree against the tree invariant after a new item is inserted."""
    new_tree.instance.instance(new_tree.to_insert)
    assert _tree_checker(getattr(new_tree.instance, ROOT_ATTR))


def test_contains(new_tree):
    """Test that tree contains all items pushed into it."""
    assert all((new_tree.instance.contains(i) for i in new_tree.sequence))


def test_contains_false(new_tree):
    """Test that tree contains all items pushed into it."""
    assert not new_tree.instance.contains(new_tree.to_insert)


def test_contains_after_insert(new_tree):
    """Check tree against the tree invariant after a new item is inserted."""
    new_tree.instance.insert(new_tree.to_insert)
    assert new_tree.instance.contains(new_tree.to_insert)


def test_size(new_tree):
    """Test that size method returns the expected size."""
    assert new_tree.instance.size() == new_tree.size


def test_depth(new_tree):
    """Test that depth method returns expected depth."""
    assert new_tree.instance.depth() == new_tree.depth


def test_balance(new_tree):
    """Test that balance method returns expected balance."""
    assert new_tree.instance.balance() == new_tree.balance


def test_left_overbalance(new_tree):
    """Test that tree becomes overbalanced to the left."""
    for item in new_tree.left_overbalance:
        new_tree.instance.insert(item)
    assert new_tree.instance.balance() > new_tree.balance


def test_right_overbalance(new_tree):
    """Test that tree becomes overbalanced to the right."""
    for item in new_tree.right_overbalance:
        new_tree.instance.insert(item)
    assert new_tree.instance.balance() < new_tree.balance


def test_no_duplicates(new_tree):
    """Test that an item cannot be inserted into the tree a second time."""
    new_tree.instance.insert(new_tree.to_insert)
    new_tree.instance.insert(new_tree.to_insert)
    assert new_tree.instance.size() == new_tree.size + 1
