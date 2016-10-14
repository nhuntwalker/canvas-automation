"""Standard test suite for the Hash Table data structure."""
from __future__ import unicode_literals

import pytest
import random
from itertools import chain, product
from collections import namedtuple
from importlib import import_module

from cases import (
    INT_EDGE_CASES,
    STR_EDGE_CASES,
    INT_TEST_CASES,
    STR_TEST_CASES,
    _make_words,
)

MODULENAME = 'hash_table'
CLASSNAME = 'HashTable'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)


REQ_METHODS = [
    'set',
    'get',
    '_hash',
]

HashTableFixture = namedtuple(
    'HashTableFixture', (
        'instance',
        'words',
        'contains',
        'to_insert',
    )
)

TEST_CASES = product(
    INT_EDGE_CASES + INT_TEST_CASES,
    chain(STR_EDGE_CASES + STR_TEST_CASES, _make_words(10, 3000)),
)


@pytest.fixture(scope='function', params=TEST_CASES)
def new_hash_table(request):
    """Return a new empty instance of MyQueue."""
    size, words = request.param
    contains = set(words)
    instance = ClassDef()

    for item in words:
        instance.insert(item)

    to_insert = 'superuniquestring'

    return HashTableFixture(
        instance,
        words,
        contains,
        to_insert,
    )


@pytest.mark.parametrize('method_name', REQ_METHODS)
def test_has_method(method_name):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method_name)
