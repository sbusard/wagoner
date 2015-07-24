#! /usr/bin/env python3

"""
The table module extract sub-word statistics from a given text and save it into
a table. This table can then be used by the word module to generate random
words.
"""

import argparse
import re
import pickle
from collections import defaultdict
from .utils import *

__all__ = ["extract_table", "check_table"]

def extract_table(words, prefix=0, flatten=False):
    """
    Given an iterable of words, return the corresponding table.
    The table is built by accumulating, for each word, for each sub-word,
    the number of occurrences of the corresponding next character.

    :param words: an iterable of strings made of alphabetic characters;
    :param prefix: if greater than 0, the maximum length of the prefix to
                   store in the table;
    :param flatten: whether to flatten the table or not;
    :return: the corresponding table.

    Example:
    >>> extract_table(['abaq'])
    {'a':{'b': 1, 'q': 1}, 'ab': {'a': 1}, 'aba': {'q': 1}, 'b': {'a': 1},
     'ba': {'q': 1}}
    """
    table = defaultdict(lambda: defaultdict(int))
    for word in words:
        word = ">" + word + "<"
        for start in range(len(word) - 1):
            maxend = len(word) - 1 if prefix <= 0 else start + prefix + 1
            for end in range(start + 1, maxend):
                subword = word[start:end]
                table[subword][word[end]] = (1 if flatten else
                                             table[subword][word[end]] + 1)
    for k,v in table.items():
        table[k] = dict(v)
    return dict(table)

def check_table(table):
    """
    Check that the given table is complete, that is, that every character of
    the table can be followed by a new character.

    :param table: the table;
    :return: True if the table is complete, False otherwise.
    """
    for character, followers in table.items():
        for follower in followers:
            if follower not in table:
                return False
    return True

def extract_words(lines):
    """
    Extract from the given iterable of lines the list of words.

    :param lines: an iterable of lines;
    :return: a generator of words of lines.
    """
    for line in lines:
       for word in re.findall(r"\w+", line):
           yield word

def process_arguments():
    """
    Process the command line arguments. The arguments are:
     * the list of texts to analyse (at least one);
     * -f (or --flatten) if the table must be flattened;
     * -o (or --output) the output file (default: stdout).
    """
    parser = argparse.ArgumentParser(description="Extract a table from the "
                                                 "given text(s)")
    parser.add_argument("text", type=argparse.FileType('r'), nargs="+",
                        help="the text to analyse")
    parser.add_argument("--prefix", "-p", type=natural, default=0,
                        dest="prefix", help="if not 0, the maximum length of "
                                            "prefixes to consider when "
                                            "choosing the next character "
                                            "(default: 0)")
    parser.add_argument("--flatten", "-f", action="store_true", default=False,
                        dest="flatten", help="flatten the table")
    parser.add_argument("--check", "-c", action="store_true", default=False,
                        dest="check", help="also check that the table is "
                                           "complete")
    parser.add_argument("--output", "-o", type=argparse.FileType('wb'),
                        default=None, dest="output",
                        help="the output destination; "
                             "if missing, print the table")
    return parser.parse_args()

if __name__ == "__main__":
    args = process_arguments()
    def all_words():
        for file in args.text:
            for word in extract_words(file):
                yield word

    table = extract_table(all_words(), prefix=args.prefix,
                          flatten=args.flatten)
    if args.check and not check_table(table):
        print("[ERROR] The given set of texts yields an incomplete table.")
    else:
        if args.output:
            pickle.dump(table, args.output)
        else:
            print(table)
