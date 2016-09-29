"""Standard tests for Trie data structure."""
from __future__ import unicode_literals

import pytest
import random
from itertools import chain
from collections import namedtuple
from importlib import import_module

from cases import STR_EDGE_CASES
MODULENAME = 'trie'
CLASSNAME = 'Trie'
ROOT_ATTR = 'root'
END_CHAR = '$'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)


REQ_METHODS = [
    'insert',
    'contains',
    'traversal',
]


TrieFixture = namedtuple(
    'TrieFixture', (
        'instance',
        'sequence',
        'contains',
        'to_insert',
        'contain_false_shorter',
        'contain_false_longer',
    )
)


def _make_words():
    """Create lists of similar words from dictionary."""
    sample_idx = random.randrange(2000)
    similar_words = []
    different_words = []

    with open('/usr/share/dict/words', 'r') as words:
        for idx, word in enumerate(words):
            word = word.strip()
            try:
                word = word.decode('utf-8')
            except AttributeError:
                pass
            if idx == sample_idx:
                different_words.append(word)
            if sample_idx <= idx <= sample_idx + 99:
                similar_words.append(word)
            elif idx > sample_idx + 99:
                yield similar_words
                sample_idx = idx + random.randrange(2000)
                similar_words = []
        yield similar_words
        yield different_words


TEST_CASES = chain((''.join(case) for case in STR_EDGE_CASES), _make_words())


@pytest.fixture(scope='function', params=TEST_CASES)
def new_trie(request):
    """Return a new empty instance of MyQueue."""
    sequence = request.param
    contains = set(sequence)
    instance = ClassDef()

    for item in sequence:
        instance.insert(item)

    to_insert = 'superuniquestring'

    longest = max(sequence, key=len) if sequence else ''
    contain_false_longer = longest + 'more'
    contain_false_shorter = longest

    while contain_false_shorter and contain_false_shorter in contains:
        contain_false_shorter = contain_false_shorter[:-1]
    if not contain_false_shorter:
        contain_false_shorter = 'superduperuniquestring'

    return TrieFixture(
        instance,
        sequence,
        contains,
        to_insert,
        contain_false_shorter,
        contain_false_longer,
    )


@pytest.mark.parametrize('method_name', REQ_METHODS)
def test_has_method(method_name):
    """Test that graph has all the correct methods."""
    assert hasattr(ClassDef(), method_name)


def test_contains_all(new_trie):
    """Check that every item in the sequence is contained within the Trie."""
    assert all((new_trie.instance.contains(val) for val in new_trie.sequence))


def test_contains_false_shorter(new_trie):
    """Check that an item similar to one in Trie but shorter returns False."""
    assert not new_trie.instance.contains(new_trie.contain_false_shorter)


def test_contains_false_longer(new_trie):
    """Check that an item similar to one in Trie but longer returns False."""
    assert not new_trie.instance.contains(new_trie.contain_false_longer)


def test_insert(new_trie):
    """Check that a new item can be inserted and then contains is true."""
    new_trie.instance.insert(new_trie.to_insert)
    assert new_trie.instance.contains(new_trie.to_insert)


def test_traversal(new_trie):
    """Check that traversal returns all items contained in the Trie."""
    assert set(new_trie.instance.traversal()) == new_trie.contains


def test_traversal_false_shorter(new_trie):
    """Check traversal doesn't return item similar but shorter."""
    assert new_trie.contain_false_shorter not in new_trie.instance.traversal()


def test_traversal_false_longer(new_trie):
    """Check traversal doesn't return item similar but longer."""
    assert new_trie.contain_false_shorter not in new_trie.instance.traversal()
