"""Standard test suite for the Hash Table data structure."""
from __future__ import unicode_literals

import pytest
import random
from itertools import chain, product
from collections import namedtuple
from importlib import import_module

from cases import (
    STR_EDGE_CASES,
    STR_TEST_CASES,
    _make_words,
)

MODULENAME = 'hash_table'
CLASSNAME = 'HashTable'
BUCKETS_ATTR = 'bucket'
GET_ERROR = True

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
        'size',
    )
)

SIZES = list(random.sample(range(1000), 20))
SIZES.extend([1, 9999])
TEST_CASES = product(
    chain(SIZES),
    chain(STR_EDGE_CASES, STR_TEST_CASES, _make_words(10, 3000)),
)

BAD_TYPES = [None, 1.0, 8, True, [], (1,), {}, set()]


@pytest.fixture(scope='function', params=TEST_CASES)
def new_hash_table(request):
    """Return a new empty instance of MyQueue."""
    size, words = request.param
    instance = ClassDef(size)
    contains = {word: word + 'val' for word in words}

    for key, val in contains.items():
        instance.set(key, val)

    to_insert = 'superuniquestring'

    return HashTableFixture(
        instance,
        words,
        contains,
        to_insert,
        size,
    )


@pytest.mark.parametrize('method_name', REQ_METHODS)
def test_has_method(method_name):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(8), method_name)


def test_hash_int(new_hash_table):
    """Test hash function returns integer."""
    val = new_hash_table.to_insert
    assert isinstance(new_hash_table.instance._hash(val), int)


def test_table_size(new_hash_table):
    """Test size of hash table."""
    val = new_hash_table.to_insert
    buckets = getattr(new_hash_table.instance, BUCKETS_ATTR)
    hashed = new_hash_table.instance._hash(val)
    assert -1 < hashed % new_hash_table.size < len(buckets)


@pytest.mark.parametrize("key", BAD_TYPES)
def test_hash_type_error(key):
    """Test that any input but string raises type error."""
    with pytest.raises(TypeError):
        ClassDef().set(key, key)


def test_get(new_hash_table):
    """Test that all previously set keys are present."""
    expected = set(new_hash_table.contains.values())
    results = set(new_hash_table.instance.get(key) for key in new_hash_table.contains)
    assert expected == results


def test_set_get(new_hash_table):
    """Test hash function sets and returns values."""
    key = new_hash_table.to_insert
    value = key + 'value'
    new_hash_table.instance.set(key, value)
    assert new_hash_table.instance.get(key) == value


def test_get_fail(new_hash_table):
    """Test table return none when key not present."""
    if GET_ERROR:
        with pytest.raises(KeyError):
            new_hash_table.instance.get(new_hash_table.to_insert)
    else:
        assert new_hash_table.instance.get(new_hash_table.to_insert) is None
