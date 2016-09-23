"""Standard tests for Trie data structure."""
from __future__ import unicode_literals

import pytest
from importlib import import_module
from itertools import chain
from collections import namedtuple

from cases import STR_EDGE_CASES, STR_TEST_CASES, MIN_STR, MAX_STR
TEST_CASES = chain(STR_EDGE_CASES, STR_TEST_CASES)

MODULENAME = 'trie'
CLASSNAME = 'Trie'
ROOT_ATTR = 'root'


module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)


REQ_METHODS = [
    'insert',
    'contains',
]


TrieFixture = namedtuple(
    'TrieFixture', (
        'instance',
        'sequence',
        'to_insert',
    )
)


def _trie_checker(tree):
    """"Help function to check trie correctness."""
    if tree is None:
        return True


@pytest.fixture(scope='function', params=TEST_CASES)
def new_trie(request):
    """Return a new empty instance of MyQueue."""
    sequence = request.param
    instance = ClassDef()

    for item in sequence:
        instance.insert(item)

    to_insert = 'superuniquestring'

    return TrieFixture(
        instance,
        sequence,
        to_insert,
    )


@pytest.mark.parametrize('method_name', REQ_METHODS)
def test_has_method(method_name):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method_name)


def test_contains_all(new_trie):
    """Check that every item in the sequence is contained within the Trie."""
    assert all((new_trie.instance.contains(val) for val in new_trie.sequence))


def test_insert(new_trie):
    """Check that a new item can be inserted and then contains is true."""
    new_trie.instance.insert(new_trie.to_insert)
    assert new_trie.instance.contains(new_trie.to_insert)
