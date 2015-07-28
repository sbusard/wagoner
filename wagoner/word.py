#! /usr/bin/env python3

"""
The word module generate, from a given table, a (set of) random words.
"""

import argparse
import pickle
import random # TODO Use cryptographic-friendly randomization
from collections import defaultdict

from wagoner.utils import *

__all__ = ["random_word", "GenerationError"]

class GenerationError(Exception):
    """
    A problem occurred during random word generation.
    """
    pass

def weighted_choices(word, table, exclude=None, flatten=False):
    """
    Return the weighted choices for word from table.

    :param word: the word (as a string);
    :param table: the table;
    :param exclude: if not None, a set of characters to exclude from the
                    weighted choices;
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
    exclude = exclude if exclude is not None else set()
    weighted_choices = defaultdict(int)
    totalsum = 1
    for start in range(len(word) - 1, -1, -1):
        currentsum = 0
        subword = word[start:]
        if subword in table:
            for successor, weight in table[subword].items():
                if successor not in exclude:
                    weight = 1 if flatten else weight
                    weight = weight * totalsum
                    weighted_choices[successor] += weight
                    currentsum += weight
        totalsum += currentsum
    return weighted_choices

def random_word(table, length, prefix=0, start=False, end=False,
                flatten=False):
    """
    Generate a random word of length from table.

    :param table: the table from which generate a random word;
    :param length: the length of the generated word; >= 1;
    :param prefix: if greater than 0, the maximum length of the prefix to
                   consider to choose the next character;
    :param start: if True, the generated word starts as a word of table;
    :param end: if True, the generated word ends as a word of table;
    :param flatten: whether or not consider the table as flattened;
    :return: a random word of length generated from table.
    :raises GenerationError: if no word of length can be generated.
    """
    if start:
        word = ">"
        length += 1
        return extend_word(table, word, length, prefix=prefix, end=end,
                           flatten=flatten)[1:]
    else:
        first_letters = list(k for k in table if len(k) == 1)
        while True:
            word = random.choice(first_letters)
            try:
                word = extend_word(table, word, length, prefix=prefix,
                                   end=end, flatten=flatten)
                return word
            except GenerationError:
                first_letters.remove(word[0])

def extend_word(table, word, length, prefix=0,end=False, flatten=False):
    """
    Extend the given word with a random suffix up to length, from table.

    :param table: the table from which generate a random word;
    :param length: the length of the extended word; >= len(word);
    :param prefix: if greater than 0, the maximum length of the prefix to
                   consider to choose the next character;
    :param end: if True, the generated word ends as a word of table;
    :param flatten: whether or not consider the table as flattened;
    :return: a random word of length generated from table, extending word.
    :raises GenerationError: if the generated word cannot be extended to
                             length.
    """
    if len(word) == length:
        if end and "<" not in table[word[-1]]:
            raise GenerationError(word + " cannot be extended")
        else:
            return word
    else:  # len(word) < length
        exclude = {"<"}
        while True:
            choices = weighted_choices(word[-prefix if prefix > 0 else 0:],
                                       table, exclude=exclude, flatten=flatten)
            if not choices:
                raise GenerationError(word + " cannot be extended")
            # Extend with the weighted choice
            character = random_weighted_choice(choices)
            word += character
            try:
                word = extend_word(table, word, length, prefix=prefix,
                                   end=end, flatten=flatten)
                return word
            except GenerationError:
                exclude.add(character)
                word = word[:-1]


def process_arguments():
    """
    Process the command line arguments. The arguments are:
     * the table to generate random from;
     * -l (or --length) for the length of generated words (default: 10);
     * -p (or --prefix) for the maximum of prefixes to consider (default: 0);
     * -c (or --count) for the number of words to generate (default: 10);
     * -s (or --start) for generating only words starting in table;
     * -e (or --end) for generating only words ending in table;
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
    parser.add_argument("--start", "-s", action="store_true", default=False,
                        dest="start", help="only starting words")
    parser.add_argument("--end", "-e", action="store_true", default=False,
                        dest="end", help="only ending words")
    parser.add_argument("--flatten", "-f", action="store_true", default=False,
                        dest="flatten", help="flatten the table")
    return parser.parse_args()

if __name__ == "__main__":
    args = process_arguments()
    table = pickle.load(args.table)
    for _ in range(args.count):
        print(random_word(table, args.length, prefix=args.prefix,
                          start=args.start, end=args.end,
                          flatten=args.flatten))
