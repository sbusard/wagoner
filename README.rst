wagoner
=======

``wagoner`` is an anagram for rawogen, a random words generator.

``wagoner`` generates random words based on a given text. A random word is
generated incrementally, and the given text is used to know which character
should follow.


Usage
-----

``wagoner`` generates random words from tables extracted from texts. You need
first to extract such a table from a text. To extract a table, use
``wagoner.table``::

    python -m wagoner.table TEXT --output text.table

This command will extract the table corresponding to ``TEXT`` into the file
``text.table``.

Then, given the extracted table, ``wagoner.word`` can extract random words::

    python -m wagoner.word text.table

This command will generate ten words of ten characters, based on the
information in ``text.table``. To generate another number of words, use the
``--count`` option and to change their length, the ``--length`` option.

Random words can also be generated from trees. While the tables only tell
the generation which character should follow, trees also ensure that the
generated word will start like a regular word (from the text it comes from) and
will end like a regular (maybe different word). Trees are built from a
table or from a text::

    python -m wagoner.tree CONTENT --output text.tree

This command will extract a tree from ``CONTENT`` and save it into the file
``text.tree``.

Warning: trees can be very large and expensive to build; to control their
complexity, you can use the ``--prefix`` and ``--length`` options. See below
for more information.


How does it work
----------------

The main idea behind wagoner is to use a text to conduct the generation of
random words. The words in the text show what usually follows a given prefix,
and this information is used to choose the next character when building a word
incrementally.

For example, given the text composed of the two words ``ambiguous`` and
``gamblings``, and the prefix ``ig``, the first word tells us that the next
character can be ``u`` (because in ``ambiguous``, the sub-word ``ig`` is
followed by ``u``), and the second word tells us that the next character can
be ``a`` or ``s`` (because in ``gamblings``, the prefix ``g`` is followed by
``a`` or ``s``). The next character is chosen randomly among the possible next
characters and the word is incrementally generated following the same rule.

This next character is chosen randomly among the possible next characters, but
weights are used to more probably use frequent characters, and longer
prefixes. In other words, when choosing the next character for the prefix
``ig``, more weight is given to ``u`` than to ``a`` and ``s`` because ``u``
follows ``ig`` in ``ambiguous`` while ``a`` and ``s`` only follow ``g`` in
``gamblings``. Furthermore, if in the given text, a character follows more
frequently a given prefix than another, the first one will have a higher
chance to be chosen. This last characteristics of the generation can be turned
down by using the ``--flatten`` option of ``wagoner.word``. If this option is
active, two characters following the same prefix will have the same chance to
be chosen; nevertheless, a character following a shorter prefix will have less
chance to be chosen than a character following a longer prefix.

This information of the frequence of successing characters in the words of
the given text is stored in tables. Note that the ``--flatten`` option is
also present with ``wagoner.table``; this forces ``wagoner.table`` to
extract a table in which the number of occurrences of a character following a
given prefix is forgotten, giving the same result as the ``--flatten`` option
of ``wagoner.word`` at generation.

Finally, when incrementally generating a random word, the full prefix is used
to extract next character. In usual languages such as English, knowing the
full prefix is not necessary to generate a pronounceable word; instead, three
or four characters are usually sufficient to choose a next character that will
sound correctly. Restricting the generation of words based on a bounded prefix
instead of the full word can be achieved by using the ``--prefix`` option of
``wagoner.word``. Similarly, the same option can be used on ``wagoner.table``
to directly generate (smaller) tables that will not propose next characters
for longer prefixes.

Trees store more information than tables, but are also tailored to more
strict generation. Trees store the information about which character should
follow a given prefix, but only for words of a given length. They also store
information to generate words starting as words of the text and ending as them.
Because of this addition information, trees can be really complex, huge and
long to generate; they can potentially store each word of a given length
generable from the table. To tackle this complexity, trees can be limited to
looking at only a suffix of the current prefix by using the ``--prefix``
option; furthermore, by building trees for shorter words (using the
``--length`` option), these trees are smaller.


Example
-------

Let's take the list of English words available on
http://www-01.sil.org/linguistics/wordlists/english/. This list contains more
than 100000 English words and should be useful to generate random words that
sound English.

First thing to do before generating random words is to extract the table::

    python -m wagoner.table wordsEn.txt --output wordsEn.table

The table is extracted and saved in the ``wordsEn.table`` file. Then, we can
generate random words::

    python -m wagoner.word wordsEn.table

that outputs, for example::

    joggeriest
    lvinistica
    cleiadicat
    zenerousne
    ulencering
    mmanencien
    zeratenesi
    keynoteric
    encientnes
    crappinesa

You can see that some words are really like real words: ``crappinesa`` really
looks like ``crappiness``, a word of ``wordsEn.txt``. To avoid generating such
too real words, we can ask wagoner to only consider finite prefixes; this will
avoid to be trapped in the increasing proability of ressembling the word
``crappiness`` as the word is generated::

    python -m wagoner.word wordsEn.table --prefix=2

that outputs, for example::

    keyelittat
    retimcenve
    quedectrot
    fodcalitur
    xcedission
    queffliqui
    eshedlerad
    ficklapett
    quatersous
    sulationur

In this case, the words are still pronounceable, but are not words of the
``wordsEn.txt`` file.

If you want to generate words that start and end the same way words of the
text start and end, you can generate a tree from the table::

    python -m wagoner.tree wordsEn.table --output=wordsEn.tree --prefix=3

The tree can then be used to generate words::

    python -m wagoner.word wordsEn.tree

that outputs, for example::

    sinationso
    disjudging
    titualimal
    avespolybd
    prophology
    japackersc
    nonneappra
    overedefra
    oxideodore
    wordshedro


Library usage
-------------

``wagoner`` can also be used as a library. ``wagoner.table.Table`` represent
tables and a table can be extracted from a text file with::

    table = Table.from_words(wagoner.utils.extract_words(text_file))

``Table.from_words`` accept two optional arguments:

* ``prefix``: if greater than 0, the length of the prefixes to take into
  account when generating the word (default is 0).
* ``flatten``: if ``True``, the table is flattened and two successing
  characters for the same prefix will have the same weight (default is
  ``False``).

From such a table, a random word can be extracted::

    word = table.random_word(word_length)

where ``word_length`` is the length of the desired word. ``random_word``
accepts several optional arguments:

* ``prefix`` and ``flatten``, as above.
* ``start``: if ``True``, the generated word starts as a word of the text
  the table is extracted from (default is ``False``).
* ``end``: if ``True``, the generated word ends as a word of the text
  the table is extracted from (default is ``False``).
  Warning: this option should not be used because it is very time consuming.

Furthermore, ``wagoner.tree.Tree`` represent trees and a tree can be
extracted from a table with::

    tree = Tree.from_table(table, word_length)

where ``table`` is a table like the one above and ``word_length`` is the
length of the words the tree will produce. Like ``Table.from_words``,
``Tree.from_table`` supports two optional arguments: ``prefix`` and
``flatten``. In this case, the ``prefix`` argument is very important
because, if set to 0 (the default value), the tree can be really huge, even
impossible to stay in memory, and will need a lot of time to be built.

From such a te, a random word can be extracted::

    word = tree.random_word()

Unlike the tables, trees contain the complete information to extract words
(their length, whether flattening the weights) and ``random_word`` takes no
optional argument (technically, it accepts any arguments, but will ignore
them).


Changelog
---------

* 1.1: support for Python 2.7.
