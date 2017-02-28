"""General test cases usable by multiple test modules."""
from __future__ import unicode_literals
import random
import string
from itertools import chain
from hashlib import md5


# Trimming off whitespace/line return chars
# reserving '0' for less-than string comparisons
# reserving '~' for greater-than string comparisons
STR_CHARS = sorted(string.printable[:-6])
STR_CHARS = STR_CHARS[1:-1]
MIN_STR = STR_CHARS[0]
MAX_STR = STR_CHARS[-1]
MAX_INT = 99999999999999999999999999
MIN_INT = -MAX_INT


def _random_with_dupes(sequence):
    """Return a random sequence including duplicates."""
    part1 = random.sample(sequence, 50)
    part2 = random.sample(part1, random.randrange(1, 50))
    result = part1 + part2
    random.shuffle(result)
    return result


INT_EDGE_CASES = [
    (),
    (0,),
    (0, 1),
    (1, 0),
    list(range(100)),
    list(range(99, -1, -1)),
    [1] * 10,
    _random_with_dupes(range(100))
]

STR_EDGE_CASES = [
    '',
    'a',
    'ab',
    'ba',
    string.ascii_letters,
    ''.join(reversed(string.ascii_letters)),
    'b' * 10,
    _random_with_dupes(STR_CHARS)
]

# lists of ints
INT_TEST_CASES = (random.sample(range(1000),
                  random.randrange(2, 20)) for n in range(10))

# strings
STR_TEST_CASES = (random.sample(STR_CHARS,
                  random.randrange(2, 20)) for n in range(10))

TEST_CASES = chain(
    INT_EDGE_CASES,
    STR_EDGE_CASES,
    INT_TEST_CASES,
    STR_TEST_CASES,
)

POP = (True, False)


def _make_words(sample_size=29, words_between_samples=2000):
    """Create lists of similar words from dictionary.

    Used for testing Trie.
    """
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


def make_unique_value():
    """Create a unique value for testing non-membership in a data strucutre."""
    return md5(b'SUPERUNIQUEFLAGVALUE').hexdigest()
