"""
The word module generate, from a given table, a (set of) random words.
"""

import argparse
import pickle
import random # TODO Use cryptographic-friendly randomization
import itertools
import bisect
from collections import defaultdict

__all__ = ["random_word", "GenerationError"]

class GenerationError(Exception):
    """
    A problem occurred during random word generation.
    """
    pass

def random_word(table, length, prefix=0, flatten=False):
    """
    Generate a random word of length from table.

    :param table: the table from which generate a random word;
    :param length: the length of the generated word; >= 1;
    :param prefix: if greater than 0, the maximum length of the prefix to
                   consider to choose the next character;
    :param flatten: whether or not consider the table as flattened;
    :return: a random word of length generated from table.
    """
    word = random.choice(list(k for k in table if len(k) == 1))
    while len(word) < length:
        # Build the weighted list of possibilities
        weighted_choices = defaultdict(int)
        totalsum = 1
        for start in range(len(word) - 1,
                           -1 if prefix <= 0 else len(word) - prefix + 1,
                           -1):
            currentsum = 0
            subword = word[start:]
            if subword in table:
                for successor, weight in table[subword].items():
                    weight = 1 if flatten else weight
                    weight = weight * totalsum
                    weighted_choices[successor] += weight
                    currentsum += weight
            totalsum += currentsum
        if not weighted_choices:
            raise GenerationError(word + " cannot be extended")

        # Extend with the weighted choice
        choices, weights = zip(*weighted_choices.items())
        cumdist = list(itertools.accumulate(weights))
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
    parser.add_argument("--length", "-l", type=int, default=10,
                        dest="length", help="the length of generated words "
                                            "(default: 10)")
    parser.add_argument("--prefix", "-p", type=int, default=0,
                        dest="prefix", help="if not 0, the maximum length of "
                                            "prefixes to consider when "
                                            "choosing the next character "
                                            "(default: 0)")
    parser.add_argument("--count", "-c", type=int, default=10,
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
