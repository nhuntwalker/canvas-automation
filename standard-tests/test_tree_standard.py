"""Standardized tests for Binary Search Tree data structure."""
from __future__ import unicode_literals

import pytest
from importlib import import_module
from collections import namedtuple, deque
from inspect import isgenerator

from cases import TEST_CASES, MIN_STR, MAX_STR, MIN_INT, MAX_INT


MODULENAME = 'bst'
CLASSNAME = 'BinaryTree'
ROOT_ATTR = 'root'
VAL_ATTR = 'value'
LEFT_ATTR = 'left'
RIGHT_ATTR = 'right'
PARENT_ATTR = 'parent'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)


REQ_METHODS = [
    'insert',
    'contains',
    'size',
    'depth',
    'balance',
    'delete',
]

TRAVERSAL_METHODS = [
    'in_order',
    'pre_order',
    'post_order',
    'breadth_first',
]

REQ_METHODS.extend(TRAVERSAL_METHODS)

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
        'to_delete',
        'sequence_after_delete',
        'depth_after_delete',
        'balance_after_delete',
        'size_after_delete',
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


def _current_less_more(sequence):
    """Return tuple of (first item, less-than items, more-than items)."""
    current = sequence[0]
    less = [i for i in sequence if i < current]
    more = [i for i in sequence if i > current]
    return current, less, more


def _unbalanced_depth(sequence):
    """Get the depth and balance from a random sequence."""
    if len(sequence) < 2:
        return len(sequence)
    current, less, more = _current_less_more(sequence)
    return max(_unbalanced_depth(less), _unbalanced_depth(more)) + 1


def _unbalanced_balance(sequence):
    """Get the depth and balance from a random sequence."""
    try:
        root, left, right = _current_less_more(sequence)
    except IndexError:
        return 0
    return _unbalanced_depth(left) - _unbalanced_depth(right)


def _in_order(sequence):
    """Get the expected in-order traversal from a random sequence."""
    if len(sequence) < 2:
        return list(sequence)
    current, less, more = _current_less_more(sequence)
    return _in_order(less) + [current] + _in_order(more)


def _pre_order(sequence):
    """Get the expected pre-order traversal from a random sequence."""
    if len(sequence) < 2:
        return list(sequence)
    current, less, more = _current_less_more(sequence)
    return [current] + _pre_order(less) + _pre_order(more)


def _post_order(sequence):
    """Get the expected post-order traversal from a random sequence."""
    if len(sequence) < 2:
        return list(sequence)
    current, less, more = _current_less_more(sequence)
    return _post_order(less) + _post_order(more) + [current]


def _breadth_first(tree):
    """Get the expected breadth-first traversal for a given tree."""
    output = []
    root = getattr(tree, ROOT_ATTR)
    if root is None:
        return output
    queue = deque([root])
    while queue:
        current = queue.pop()
        output.append(getattr(current, VAL_ATTR))
        for attr_name in (LEFT_ATTR, RIGHT_ATTR):
            node = getattr(current, attr_name)
            if node is not None:
                queue.appendleft(node)
    return output


# Test deleting every single item in every single test case.

def _setup_to_delete(cases):
    """Setup tests to delete every possible item in test sequence."""
    for sequence in cases:
        if not sequence:
            yield (sequence, None)
        else:
            for item in sequence:
                yield (sequence, item)


@pytest.fixture(scope='function', params=_setup_to_delete(TEST_CASES))
def new_tree(request):
    """Return a new empty instance of MyQueue."""
    sequence, to_delete = request.param
    instance = ClassDef()
    size = len(set(sequence))

    for item in sequence:
        instance.insert(item)

    depth = _unbalanced_depth(sequence)
    balance = _unbalanced_balance(sequence)

    if not sequence or isinstance(sequence[0], int):
        left_overbalance = range(MIN_INT, MIN_INT - 100, -1)
        right_overbalance = range(MAX_INT, MAX_INT + 100)
        to_insert = MAX_INT
    else:
        left_overbalance = (MIN_STR * n for n in range(100, 0, -1))
        right_overbalance = (MAX_STR * n for n in range(1, 101))
        to_insert = 'superuniquestring'

    sequence_after_delete = list(sequence)
    try:
        sequence_after_delete.remove(to_delete)
    except ValueError:
        pass
    size_after_delete = len(set(sequence_after_delete))
    depth_after_delete = _unbalanced_depth(sequence_after_delete)
    balance_after_delete = _unbalanced_balance(sequence_after_delete)

    return BinaryTreeFixture(
        instance,
        sequence,
        size,
        depth,
        balance,
        left_overbalance,
        right_overbalance,
        to_insert,
        to_delete,
        sequence_after_delete,
        depth_after_delete,
        balance_after_delete,
        size_after_delete,
    )


@pytest.mark.parametrize('method_name', REQ_METHODS)
def test_has_method(method_name):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method_name)


def test_invariant(new_tree):
    """Check tree against the tree invariant."""
    assert _tree_checker(getattr(new_tree.instance, ROOT_ATTR))


def test_invariant_after_insert(new_tree):
    """Check tree against the tree invariant after a new item is inserted."""
    new_tree.instance.insert(new_tree.to_insert)
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


# Traversal tests


@pytest.mark.parametrize('method_name', TRAVERSAL_METHODS)
def test_traversal_generator(method_name, new_tree):
    """Test that all traversal methods always return generators."""
    method = getattr(new_tree.instance, method_name)
    assert isgenerator(method())


@pytest.mark.parametrize('method_name', TRAVERSAL_METHODS[:-1])
def test_traversals(method_name, new_tree):
    """Test that in-order traversal generates values in sorted order."""
    method = getattr(new_tree.instance, method_name)
    canon = globals()['_' + method_name]
    assert list(method()) == canon(new_tree.sequence)


def test_breadth_first(new_tree):
    """Test that breadth first traversal happens as expected."""
    expected = _breadth_first(new_tree.instance)
    assert list(new_tree.instance.breadth_first()) == expected


# Deletion tests


def test_delete_not_in_tree(new_tree):
    """Test that trying to delete something not in the tree does nothing."""
    new_tree.instance.delete(new_tree.to_insert)
    assert all([new_tree.instance.size() == new_tree.size,
                new_tree.instance.depth() == new_tree.depth,
                new_tree.instance.balance() == new_tree.balance])


def test_invariant_after_delete(new_tree):
    """Test that tree still conforms to invariant after deletion."""
    new_tree.instance.delete(new_tree.to_delete)
    assert _tree_checker(getattr(new_tree.instance, ROOT_ATTR))


def test_deleted_not_contained(new_tree):
    """Test that deleted item is not in the tree after deletion."""
    new_tree.instance.delete(new_tree.to_delete)
    assert not new_tree.instance.contains(new_tree.to_delete)


def test_contains_after_delete(new_tree):
    """Test that all other items are still contained by tree after deletion."""
    new_tree.instance.delete(new_tree.to_delete)
    assert all([new_tree.instance.contains(item)
                for item in new_tree.sequence_after_delete])


def test_size_after_delete(new_tree):
    """Test that tree size is correct after deletion of item."""
    new_tree.instance.delete(new_tree.to_delete)
    assert new_tree.instance.size() == new_tree.size_after_delete


# def test_depth_after_delete(new_tree):
#     """Test that tree size is correct after deletion of item."""
#     new_tree.instance.delete(new_tree.to_delete)
#     assert new_tree.instance.depth() == new_tree.depth_after_delete


# def test_balance_after_delete(new_tree):
#     """Test that tree balance is correct after deletion of item."""
#     new_tree.instance.delete(new_tree.to_delete)
#     assert new_tree.instance.balance() == new_tree.balance_after_delete


# node can be added then deleted;
