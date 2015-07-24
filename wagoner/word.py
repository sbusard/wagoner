#! /usr/bin/env python3

"""
The word module generate, from a given table, a (set of) random words.
"""

import argparse
import pickle
import random # TODO Use cryptographic-friendly randomization
import bisect
from collections import defaultdict
from utils import *

__all__ = ["random_word", "GenerationError"]

class GenerationError(Exception):
    """
    A problem occurred during random word generation.
    """
    pass

def weighted_choices(word, table, flatten=False):
    """
    Return the weighted choices for word from table.

    :param word: the word (as a string);
    :param table: the table;
    :param flatten: whether or not consider the table as flattened;
    :return: the weighted choices for word from table.

    The weighted choices are computed such that:
    * for a given suffix of word, the possible choices are the ones defined by
      table;
    * the weights of these possible choices are either 1 if flatten is True,
      or the weights defined by table otherwise;
    * the weights are accumulated for each suffix, but longer suffixes have
      scaled up weights to assure that all shorter suffixes will have less
      probabilities to be picked.
    """
    weighted_choices = defaultdict(int)
    totalsum = 1
    for start in range(len(word) - 1, -1, -1):
        currentsum = 0
        subword = word[start:]
        if subword in table:
            for successor, weight in table[subword].items():
                weight = 1 if flatten else weight
                weight = weight * totalsum
                weighted_choices[successor] += weight
                currentsum += weight
        totalsum += currentsum
    return weighted_choices

def random_word(table, length, prefix=0, flatten=False):
    """
    Generate a random word of length from table.

    :param table: the table from which generate a random word;
    :param length: the length of the generated word; >= 1;
    :param prefix: if greater than 0, the maximum length of the prefix to
                   consider to choose the next character;
    :param flatten: whether or not consider the table as flattened;
    :return: a random word of length generated from table.
    :raises GenerationError: if the generated word cannot be extended to
                             length.
    """
    word = random.choice(list(k for k in table if len(k) == 1))
    while len(word) < length:
        # Build the weighted list of possibilities
        choices = weighted_choices(word[-prefix if prefix > 0 else 0:],
                                   table, flatten=flatten)
        if not choices:
            raise GenerationError(word + " cannot be extended")

        # Extend with the weighted choice
        choices, weights = zip(*choices.items())
        cumdist = list(accumulate(weights))
        x = random.random() * cumdist[-1]
        word +=choices[bisect.bisect(cumdist, x)]
    return word

def process_arguments():
    """
    Process the command line arguments. The arguments are:
     * the table to generate random from;
     * -l (or --length) for the length of generated words (default: 10);
     * -p (or --prefix) for the maximum of prefixes to consider (default: 0);
     * -c (or --count) for the number of words to generate (default: 10);
     * -f (or --flatten) if the table must be flattened before generation.
    """
    parser = argparse.ArgumentParser(description="Generate random words from "
                                                 "the given table")
    parser.add_argument("table", type=argparse.FileType('rb'),
                        help="the table")
    parser.add_argument("--length", "-l", type=nonzero_natural, default=10,
                        dest="length", help="the length of generated words "
                                            "(default: 10)")
    parser.add_argument("--prefix", "-p", type=natural, default=0,
                        dest="prefix", help="if not 0, the maximum length of "
                                            "prefixes to consider when "
                                            "choosing the next character "
                                            "(default: 0)")
    parser.add_argument("--count", "-c", type=natural, default=10,
                        dest="count", help="the number of words to generate "
                                           "(default: 10)")
    parser.add_argument("--flatten", "-f", action="store_true", default=False,
                        dest="flatten", help="flatten the table")
    return parser.parse_args()

if __name__ == "__main__":
    args = process_arguments()
    table = pickle.load(args.table)
    for _ in range(args.count):
        print(random_word(table, args.length, prefix=args.prefix,
                          flatten=args.flatten))
