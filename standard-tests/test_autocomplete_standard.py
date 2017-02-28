"""Standard tests for Trie data structure."""
from __future__ import unicode_literals

import pytest
import random
from itertools import chain
from collections import namedtuple
from importlib import import_module

from cases import STR_EDGE_CASES
MODULENAME = 'autocomplete'
CLASSNAME = 'Autocompleter'
END_CHAR = '$'

module = import_module(MODULENAME)
ClassDef = getattr(module, CLASSNAME)


AutocompleteFixture = namedtuple(
    'AutocompleteFixture', (
        'instance',
        'sequence',
        'contains',
        'contain_false_shorter',
        'contain_false_longer',
        'start',
        'traverse',
        'max_completions',
    )
)


def _make_words():
    """Create lists of similar words from dictionary."""
    sample_size = 29
    words_between_samples = 2000

    sample_idx = random.randrange(words_between_samples)
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
            if sample_idx <= idx <= sample_idx + sample_size:
                similar_words.append(word)
            elif idx > sample_idx + sample_size:
                yield similar_words
                sample_idx = idx + random.randrange(words_between_samples)
                similar_words = []
        yield similar_words
        yield different_words


def _start_stubs(sequence):
    """Generate many start points for each item in a sequence."""
    for word in sequence:
        num_starts = min(3, len(word))
        start_range = range(min(1, len(word)), len(word) + 1)
        for size in random.sample(start_range, num_starts):
            yield word[:size]


TEST_CASES = chain(
    (''.join(case) for case in STR_EDGE_CASES if END_CHAR not in case),
    _make_words(),
)
TEST_CASES = ((sequence, start) for sequence in TEST_CASES
              for start in _start_stubs(sequence))


@pytest.fixture(scope='function', params=TEST_CASES)
def new_ac(request):
    """Return a new empty instance of MyQueue."""
    sequence, start = request.param
    max_completions = random.randrange(10)

    contains = set(sequence)
    instance = ClassDef(sequence, max_completions)

    longest = max(sequence, key=len) if sequence else ''
    contain_false_longer = longest + 'more'
    contain_false_shorter = longest

    while contain_false_shorter and contain_false_shorter in contains:
        contain_false_shorter = contain_false_shorter[:-1]
    if not contain_false_shorter:
        contain_false_shorter = 'superduperuniquestring'

    traverse = set(word for word in sequence if word.startswith(start))

    return AutocompleteFixture(
        instance,
        sequence,
        contains,
        contain_false_shorter,
        contain_false_longer,
        start,
        traverse,
        max_completions,
    )


def test_max_completions_default():
    """Check that max_completions is set to 5 by default."""
    instance = ClassDef([])
    assert instance.max_completions == 5


def test_num_completions(new_ac):
    """Check that the correct number of autocompletions are returned."""
    results = new_ac.instance(new_ac.start)
    assert len(results) <= new_ac.max_completions


def test_correct_results(new_ac):
    """Check that the results are a subset of the expected results."""
    results = new_ac.instance(new_ac.start)
    assert set(results).issubset(new_ac.contains)


def test_contains_false_shorter(new_ac):
    """Check that an item similar to one in Trie but shorter returns False."""
    results = new_ac.instance(new_ac.start)
    assert new_ac.contain_false_shorter not in results


def test_contains_false_longer(new_ac):
    """Check that an item similar to one in Trie but longer returns False."""
    results = new_ac.instance(new_ac.start)
    assert new_ac.contain_false_longer not in results
