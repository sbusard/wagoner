#! /usr/bin/env python3

"""
The table module extract sub-word statistics from a given text and save it into
a table. This table can then be used by the word module to generate random
words.
"""

import argparse
import pickle
from collections import defaultdict, Mapping
import random # TODO Use cryptographic-friendly randomization
from wagoner.utils import *

__all__ = ["table"]

class table(Mapping):
    """
    A table is a mapping of strings to mapping of their successing characters,
    with the weight of the corresponding character. That is, given t a table,
    t[s][c] gives the weight of c following s. Note that only non-zero weights
    are present.
    """

    def __init__(self, table):
        """
        Create a new table from table content.

        :param table: the content of the new table.
        """
        self.__content = table

    @classmethod
    def from_words(cls, words, prefix=0, flatten=False):
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
        t = defaultdict(lambda: defaultdict(int))
        for word in words:
            word = ">" + word + "<"
            for start in range(len(word) - 1):
                maxend = len(word) - 1 if prefix <= 0 else start + prefix + 1
                for end in range(start + 1, maxend + 1):
                    subword = word[start:end]
                    t[subword][word[end]] = (1 if flatten else
                                             t[subword][word[end]] + 1)
        for k,v in t.items():
            t[k] = dict(v)
        return cls(dict(t))

    def __getitem__(self, key):
        return self.__content[key]

    def __iter__(self):
        return iter(self.__content)

    def __len__(self):
        return len(self.__content)

    def check(self):
        """
        Check that this table is complete, that is, every character of this
        table can be followed by a new character.

        :return: True if the table is complete, False otherwise.
        """
        for character, followers in self.items():
            for follower in followers:
                if follower not in self:
                    return False
        return True

    def weighted_choices(self, word, exclude=None, flatten=False):
        """
        Return the weighted choices for word from this table.
        
        :param word: the word (as a string);
        :param exclude: if not None, a set of characters to exclude from the
                        weighted choices;
        :param flatten: whether or not consider this table as flattened;
        :return: the weighted choices for word from this table.
        
        The weighted choices are computed such that:
        * for a given suffix of word, the possible choices are the ones defined
          by table;
        * the weights of these possible choices are either 1 if flatten is
          True, or the weights defined by table otherwise;
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
            if subword in self:
                for successor, weight in self[subword].items():
                    if successor not in exclude:
                        weight = 1 if flatten else weight
                        weight = weight * totalsum
                        weighted_choices[successor] += weight
                        currentsum += weight
            totalsum += currentsum
        return weighted_choices

    def random_word(self, length, prefix=0, start=False, end=False,
                    flatten=False):
        """
        Generate a random word of length from this table.

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
            return self._extend_word(word, length, prefix=prefix, end=end,
                                     flatten=flatten)[1:]
        else:
            first_letters = list(k for k in self if len(k) == 1)
            while True:
                word = random.choice(first_letters)
                try:
                    word = self._extend_word(word, length, prefix=prefix,
                                             end=end, flatten=flatten)
                    return word
                except GenerationError:
                    first_letters.remove(word[0])

    def _extend_word(self, word, length, prefix=0,end=False, flatten=False):
        """
        Extend the given word with a random suffix up to length.

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
            if end and "<" not in self[word[-1]]:
                raise GenerationError(word + " cannot be extended")
            else:
                return word
        else:  # len(word) < length
            exclude = {"<"}
            while True:
                choices = self.weighted_choices(word[-prefix
                                                     if prefix > 0
                                                     else 0:],
                                                exclude=exclude,
                                                flatten=flatten)
                if not choices:
                    raise GenerationError(word + " cannot be extended")
                # Extend with the weighted choice
                character = random_weighted_choice(choices)
                word += character
                try:
                    word = self._extend_word(word, length, prefix=prefix,
                                             end=end, flatten=flatten)
                    return word
                except GenerationError:
                    exclude.add(character)
                    word = word[:-1]

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

    t = table.from_words(all_words(), prefix=args.prefix, flatten=args.flatten)
    if args.check and not t.check():
        print("[ERROR] The given set of texts yields an incomplete table.")
    else:
        if args.output:
            pickle.dump(t, args.output)
        else:
            print(t)
