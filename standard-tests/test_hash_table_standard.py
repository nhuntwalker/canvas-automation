"""Standard test suite for the Hash Table data structure."""
from __future__ import unicode_literals

import pytest
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
BUCKETS_ATTR = 'buckets'

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

BAD_TYPES = [None, 1.0, 8, True, [], (1,), {}, set()]


@pytest.fixture(scope='function', params=TEST_CASES)
def new_hash_table(request):
    """Return a new empty instance of MyQueue."""
    size, words = request.param
    contains = set(words)
    instance = ClassDef(size)

    for item in words:
        instance.set(item, item + 'value')

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


def test_hash_int(new_hash_table):
    """Test hash function returns integer."""
    val = new_hash_table.to_insert
    assert isinstance(new_hash_table.instance._hash(val), int)


def test_table_size(new_hash_table, value):
    """Test size of hash table."""
    buckets = getattr(new_hash_table.instance, BUCKETS_ATTR)
    assert -1 < new_hash_table.instance._hash(value) < len(buckets)


@pytest.mark.parametrize("value", BAD_TYPES)
def test_hash_type_error(new_hash_table, value):
    """Test that any input but string raises type error."""
    with pytest.raises(TypeError):
        new_hash_table.instance._hash(value)


def test_set_get(new_hash_table):
    """Test hash function sets and returns values."""
    key = new_hash_table.to_insert
    value = key + 'value'
    new_hash_table.instance.set(key, value)
    assert new_hash_table.instance.get(key) == value


def test_get_fail(new_hash_table):
    """Test table return none when key not present."""
    assert new_hash_table.instance.get(new_hash_table.to_insert) is None
