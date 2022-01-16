import json
import importlib.resources
import random

_nouns = None

_adjs = None


def get_nouns():
    """Return list of all nouns."""
    global _nouns
    if _nouns is None:
        resource = importlib.resources.files(__package__) / "nouns.json"
        with resource.open('r') as f:
            _nouns = json.load(f)
    return _nouns


def get_adjectives():
    """Return list of all adjectives."""
    global _adjs
    if _adjs is None:
        resource = importlib.resources.files(__package__) / "adjectives.json"
        with resource.open('r') as f:
            _adjs = json.load(f)
    return _adjs


def _get_a_word(words, length=None, bound='exact', seed=None):
    """Return a random word.

    :param list words: A list of words
    :param int length: Maximal length of requested word
    :param bound: Whether to interpret length as upper or exact bound
    :type bound: A string 'exact' or 'atmost'
    :param seed: A seed for random number generator
    :rtype: str

    """
    assert bound in ['exact', 'atmost']

    if seed is not None:
        random.seed(a=seed)

    if length is None:
        return random.choice(words)

    def is_len_exact(s):
        return len(s) == length

    def is_len_atmost(s):
        return len(s) <= length

    is_len = is_len_exact if bound == 'exact' else is_len_atmost

    try:
        return random.choice(list(filter(is_len, words)))
    except IndexError:
        return None


def get_a_noun(length=None, bound='exact', seed=None):
    """Return a random noun.

    :param int length: Maximal length of requested word
    :param bound: Whether to interpret length as upper or exact bound
    :type bound: A string 'exact' or 'atmost'
    :param seed: A seed for random number generator
    :rtype: str
    """
    return _get_a_word(get_nouns(), length=length, bound=bound, seed=seed)


def get_an_adjective(length=None, bound='exact', seed=None):
    """Return a random adjective.

    :param int length: Maximal length of requested word
    :param bound: Whether to interpret length as upper or exact bound
    :type bound: A string 'exact' or 'atmost'
    :param seed: A seed for random number generator
    :rtype: str
    """
    return _get_a_word(get_adjectives(), length=length, bound=bound, seed=seed)
