"""
A set of utility functions.
"""

import bisect
import operator
import random

__all__ = ["accumulate", "natural", "nonzero_natural",
           "random_weighted_choice"]

def accumulate(iterable, func=operator.add):
    'Return running totals'
    # Copied from
    # https://docs.python.org/3/library/itertools.html#itertools.accumulate
    # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
    # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
    it = iter(iterable)
    total = next(it)
    yield total
    for element in it:
        total = func(total, element)
        yield total

def natural(value):
    """
    Return value as a positive integer.
    
    :param value: the value to cast;
    :return: value as a positive integer.
    :raises ValueError: if value does not represent a positive integer.
    """
    integer = int(value)
    if integer < 0:
        raise ValueError("'%s' is not a positive integer" % value)
    return integer

def nonzero_natural(value):
    """
    Return value as a strict positive integer.
    
    :param value: the value to cast;
    :return: value as a strict positive integer.
    :raises ValueError: if value does not represent a strict positive integer.
    """
    integer = int(value)
    if integer <= 0:
        raise ValueError("'%s' is not a strict positive integer" % value)
    return integer


def random_weighted_choice(choices):
    """
    Return a random key of choices, weighted by their value.

    :param choices: a dictionary of keys and positive integer pairs;
    :return: a random key of choices.
    """
    choices, weights = zip(*choices.items())
    cumdist = list(accumulate(weights))
    x = random.random() * cumdist[-1]
    element = bisect.bisect(cumdist, x)
    return choices[element]
