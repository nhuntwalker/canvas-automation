"""Standardized tests for Binary Search Tree data structure."""
from __future__ import unicode_literals

# proper test for each traversal
# invariant balance traverse

import math
import pytest
import random
from importlib import import_module
from collections import namedtuple, deque
from inspect import isgenerator

from cases import TEST_CASES, MIN_STR, MAX_STR, MIN_INT, MAX_INT


"""
Match MODULENAME and CLASSNAME to student.

Comment in lines as appropriate for steps following inital.
All previous test should continue to pass with new steps.

Traversals:
    -REQ_METHODS.extend
    -Traversal tests

Deletion:
    -delete in REQ_METHODS
    -tests under deletion header

Balancing:
    -Set BALANCED = True
"""


BALANCED = False
MODULENAME = 'bst'
CLASSNAME = 'BinarySearchTree'
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
    # 'delete',
]

TRAVERSAL_METHODS = [
    'in_order',
    'pre_order',
    'post_order',
    'breadth_first',
]

# REQ_METHODS.extend(TRAVERSAL_METHODS)

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
        'contains_after_delete',
        'depth_after_delete',
        'balance_after_delete',
        'size_after_delete',
        'to_delete_half',
        'contains_after_delete_half',
        'depth_after_delete_half',
        'balance_after_delete_half',
        'size_after_delete_half',
    )
)


def _tree_checker(node):
    """"Help function to check binary tree correctness."""
    if node is None:
        return True

    this_val = getattr(node, VAL_ATTR)
    left = getattr(node, LEFT_ATTR)
    right = getattr(node, RIGHT_ATTR)

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


def _unbalanced_depth_root(sequence):
    """Get the depth and balance from a random sequence."""
    if len(sequence) < 2:
        return 0
    current, less, more = _current_less_more(sequence)
    return max(_unbalanced_depth(less), _unbalanced_depth(more))


def _unbalanced_depth(sequence):
    """Get the depth and balance from a random sequence."""
    if len(sequence) < 2:
        return len(sequence)
    current, less, more = _current_less_more(sequence)
    return max(_unbalanced_depth(less), _unbalanced_depth(more)) + 1


def _balance(sequence):
    """Get the depth and balance from a random sequence."""
    try:
        root, left, right = _current_less_more(sequence)
    except IndexError:
        return 0
    return _unbalanced_depth(left) - _unbalanced_depth(right)


def _depth(node):
    if node is None:
        return 0
    return max(_depth(x) for x in (node.getattr(node, LEFT_ATTR),
                                   node.getattr(node, RIGHT_ATTR))) + 1


def _in_order(node, return_vals=True):
    """Get expected in-order traversal from a node in a Binary Search Tree."""
    if node is None:
        return []
    if return_vals:
        val = getattr(node, VAL_ATTR)
    else:
        val = node
    left = getattr(node, LEFT_ATTR)
    right = getattr(node, RIGHT_ATTR)
    return _in_order(left, return_vals) + [val] + _in_order(right, return_vals)


def _pre_order(node):
    """Get the expected pre-order traversal from a random sequence."""
    if node is None:
        return []
    val = getattr(node, VAL_ATTR)
    left = getattr(node, LEFT_ATTR)
    right = getattr(node, RIGHT_ATTR)
    return [val] + _pre_order(left) + _pre_order(right)


def _post_order(node):
    """Get the expected post-order traversal from a random sequence."""
    if node is None:
        return []
    val = getattr(node, VAL_ATTR)
    left = getattr(node, LEFT_ATTR)
    right = getattr(node, RIGHT_ATTR)
    return _post_order(left) + _post_order(right) + [val]


def _breadth_first(root):
    """Get the expected breadth-first traversal for a given tree."""
    output = []
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

    if BALANCED:
        try:
            depth = math.floor(math.log(size, 2)) + 1
        except ValueError:
            depth = 0
        balance = _balance(sequence)
    else:
        depth = _unbalanced_depth_root(sequence)
        balance = _balance(sequence)

    if not sequence or isinstance(sequence[0], int):
        left_overbalance = range(MIN_INT, MIN_INT - 100, -1)
        right_overbalance = range(MAX_INT, MAX_INT + 100)
        to_insert = MAX_INT
    else:
        left_overbalance = (MIN_STR * n for n in range(100, 0, -1))
        right_overbalance = (MAX_STR * n for n in range(1, 101))
        to_insert = 'superuniquestring'

    contains_after_delete = set(sequence)
    try:
        contains_after_delete.remove(to_delete)
    except KeyError:
        pass
    size_after_delete = len(contains_after_delete)

    sequence_after_delete = list(sequence)
    while to_delete in sequence_after_delete:
        sequence_after_delete.remove(to_delete)
    depth_after_delete = _unbalanced_depth(sequence_after_delete)
    balance_after_delete = _balance(sequence_after_delete)

    contains_after_delete_half = set(sequence)
    to_delete_half = []
    sequence_after_delete_half = list(sequence)
    for _ in range(len(sequence) // 2):
        item = random.choice(sequence_after_delete_half)
        sequence_after_delete_half.remove(item)
        to_delete_half.append(item)
    try:
        for i in to_delete_half:
            contains_after_delete_half.remove(i)
    except KeyError:
        pass
    size_after_delete_half = len(contains_after_delete_half)

    depth_after_delete_half = _unbalanced_depth(sequence_after_delete_half)
    balance_after_delete_half = _balance(sequence_after_delete_half)

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
        contains_after_delete,
        depth_after_delete,
        balance_after_delete,
        size_after_delete,
        to_delete_half,
        contains_after_delete_half,
        depth_after_delete_half,
        balance_after_delete_half,
        size_after_delete_half,
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
    assert all([new_tree.instance.contains(i) for i in new_tree.sequence])


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
    if BALANCED:
        assert abs(new_tree.instance.depth() - new_tree.depth) < 2
    else:
        assert new_tree.instance.depth() == new_tree.depth


def test_balance(new_tree):
    """Test that balance method returns expected balance."""
    if BALANCED:
        assert -2 < new_tree.instance.balance() < 2
    else:
        assert new_tree.instance.balance() == new_tree.balance


def test_left_overbalance(new_tree):
    """Test that tree becomes overbalanced to the left."""
    for item in new_tree.left_overbalance:
        new_tree.instance.insert(item)
    if BALANCED:
        assert -2 < new_tree.instance.balance() < 2
    else:
        assert new_tree.instance.balance() > new_tree.balance


def test_right_overbalance(new_tree):
    """Test that tree becomes overbalanced to the right."""
    for item in new_tree.right_overbalance:
        new_tree.instance.insert(item)
    if BALANCED:
        assert -2 < new_tree.instance.balance() < 2
    else:
        assert new_tree.instance.balance() < new_tree.balance


def test_no_duplicates(new_tree):
    """Test that an item cannot be inserted into the tree a second time."""
    new_tree.instance.insert(new_tree.to_insert)
    new_tree.instance.insert(new_tree.to_insert)
    assert new_tree.instance.size() == new_tree.size + 1


# # Traversal tests


# @pytest.mark.parametrize('method_name', TRAVERSAL_METHODS)
# def test_traversal_generator(method_name):
#     """Test that all traversal methods always return generators."""
#     method = getattr(ClassDef(), method_name)
#     assert isgenerator(method())


# @pytest.mark.parametrize('method_name', TRAVERSAL_METHODS)
# def test_traversals(method_name, new_tree):
#     """Test that in-order traversal generates values in sorted order."""
#     canon = globals()['_' + method_name]
#     method = getattr(new_tree.instance, method_name)
#     root = getattr(new_tree.instance, ROOT_ATTR)
#     assert list(method()) == canon(root)


# # Deletion tests


# def test_delete_not_in_tree(new_tree):
#     """Test that trying to delete something not in the tree does nothing."""
#     new_tree.instance.delete(new_tree.to_insert)
#     size_check = new_tree.instance.size() == new_tree.size
#     if BALANCED:
#         depth_check = abs(new_tree.instance.depth() - new_tree.depth) < 2
#     else:
#         depth_check = new_tree.instance.depth() == new_tree.depth
#     assert all([size_check, depth_check])


# def test_invariant_after_delete(new_tree):
#     """Test that tree still conforms to invariant after deletion."""
#     new_tree.instance.delete(new_tree.to_delete)
#     assert _tree_checker(getattr(new_tree.instance, ROOT_ATTR))


# def test_deleted_not_contained(new_tree):
#     """Test that deleted item is not in the tree after deletion."""
#     new_tree.instance.delete(new_tree.to_delete)
#     assert not new_tree.instance.contains(new_tree.to_delete)


# def test_contains_after_delete(new_tree):
#     """Test contents of the tree after deletion."""
#     new_tree.instance.delete(new_tree.to_delete)
#     assert all([new_tree.instance.contains(item)
#                 for item in new_tree.contains_after_delete])


# def test_size_after_delete(new_tree):
#     """Test that tree size is correct after deletion of item."""
#     new_tree.instance.delete(new_tree.to_delete)
#     assert new_tree.instance.size() == new_tree.size_after_delete


# def test_depth_after_delete(new_tree):
#     """Test that tree size is correct after deletion of item."""
#     if not BALANCED and not new_tree.size:
#         pytest.skip()
#     new_tree.instance.delete(new_tree.to_delete)
#     try:
#         depth = int(math.floor(math.log(new_tree.size_after_delete, 2)) + 1)
#     except ValueError:
#         depth = 0
#     if BALANCED:
#         assert int(abs(new_tree.instance.depth() - depth)) < 2
#     else:
#         assert new_tree.instance.depth() == depth


# def test_balance_after_delete(new_tree):
#     """Test that tree balance is correct after deletion of item."""
#     if not BALANCED and not new_tree.size:
#         pytest.skip()
#     new_tree.instance.delete(new_tree.to_delete)
#     if BALANCED:
#         assert -2 < new_tree.instance.balance() < 2
#     else:
#         assert new_tree.instance.balance() == new_tree.balance_after_delete


# def test_depth_after_delete_half(new_tree):
#     """Test that tree depth is correct after deletion of many items."""
#     if not BALANCED and len(new_tree.sequence) < 2:
#         pytest.skip()
#     for i in new_tree.to_delete_half:
#         new_tree.instance.delete(i)
#     try:
#         depth = math.log(new_tree.size_after_delete_half // 2, 2)
#         depth = int(math.floor(depth) + 1)
#     except ValueError:
#         depth = 0
#     if BALANCED:
#         assert abs(new_tree.instance.depth() - depth) < 2
#     else:
#         assert new_tree.instance.depth() == depth


# def test_balance_after_delete_half(new_tree):
#     """Test that tree balance is good after deletion of many items."""
#     if not BALANCED and not new_tree.size:
#         pytest.skip()
#     for i in new_tree.to_delete_half:
#         new_tree.instance.delete(i)
#     if BALANCED:
#         assert -2 < new_tree.instance.balance() < 2
#     else:
#         balance = new_tree.balance_after_delete_half
#         assert new_tree.instance.balance() == balance


# def test_all_subtrees_balanced(new_tree):
#     """Test tree is balanced at every node."""
#     if not BALANCED or len(new_tree.sequence) < 2:
#         pytest.skip()

#     # check the balance at every node/subtree
#     for node in _in_order(getattr(new_tree.instance,
#                           ROOT_ATTR), return_vals=False):
#         left = _depth(getattr(node, LEFT_ATTR))
#         right = _depth(getattr(node, RIGHT_ATTR))
#         assert -2 < (left - right) < 2


# def test_all_subtrees_balances_after_delete_half(new_tree):
#     """Test that tree is balanced after deletion of many items."""
#     if not BALANCED or len(new_tree.sequence) < 2:
#         pytest.skip()

#     for i in new_tree.to_delete_half:
#         new_tree.instance.delete(i)

#     # check the balance at every node/subtree
#     for node in _in_order(getattr(new_tree.instance, ROOT_ATTR),
#                           return_vals=False):
#         left = _depth(getattr(node, LEFT_ATTR))
#         right = _depth(getattr(node, RIGHT_ATTR))
#         assert -2 < (left - right) < 2
