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


def _make_words():
    """Create lists of similar words from dictionary."""
    active_idx = random.randrange(2000)
    output_words = []
    with open('/usr/share/dict/words') as words:
        for idx, word in enumerate(words):
            word = word.strip()
            if active_idx <= idx <= active_idx + 99:
                output_words.append(word)
            elif idx > active_idx + 99:
                yield output_words
                active_idx = idx + random.randrange(2000)
                output_words = []
        yield output_words


TEST_CASES = chain((''.join(case) for case in STR_EDGE_CASES), _make_words())


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
