wagoner
=======

``wagoner`` is an anagram for rawogen, a random words generator.

``wagoner`` generates random words based on a given text. A random word is generated incrementally, and the given text is used to know which character should follow.


Usage
-----

``wagoner`` generates random words from tables extracted from texts. You need first to extract such a table from a text. To extract a table, use ``wagoner.table``::

    python -m wagoner.table TEXT --output text.table

This command will extract the table corresponding to ``TEXT`` into the file ``text.table``.

Then, given the extracted table, ``wagoner.word`` can extract random words::

    python -m wagoner.word text.table

This command will generate ten words of ten characters, based on the information in ``text.table``. To generate another number of words, use the ``--count`` option and to change their length, the ``--length`` option.


How does it work
----------------

The main idea behind wagoner is to use a given (set of) text(s) to conduct the generation of random words. The words in the text show what usually follows a given prefix, and this information is used to choose the next character when building a word incrementally.

For example, given the text composed of the two words ``ambiguous`` and ``gamblings``, and the prefix ``ig``, the first word tells us that the next character can be ``u`` (because in ``ambiguous``, the sub-word ``ig`` is followed by ``u``), and the second word tells us that the next character can be ``a`` or ``s`` (because in ``gamblings``, the prefix ``g`` is followed by ``a`` or ``s``). The next character is chosen randomly among the possible next characters and the word is incrementally generated following the same rule.

This next character is chosen randomly among the possible next characters, but weights are used to more probably use frequent characters, and longer prefixes. In other words, when choosing the next character for the prefix ``ig``, more weight is given to ``u`` than to ``a`` and ``s`` because ``u`` follows ``ig`` in ``ambiguous`` while ``a`` and ``s`` only follow ``g`` in ``gamblings``. Furthermore, if in the given text, a character follows more frequently a given prefix than another, the first one will have a higher chance to be chosen. This last characteristics of the generation can be turned down by using the ``--flatten`` option of ``wagoner.word``. If this option is active, two characters following the same prefix will have the same chance to be chosen; nevertheless, a character following a shorter prefix will have less chance to be chosen than a character following a longer prefix.

Note that the ``--flatten`` option is also present with ``wagoner.table``; this forces ``wagoner.table`` to extract a table in which the number of occurrences of a character following a given prefix is forgotten, giving the same result as the ``--flatten`` option of ``wagoner.word`` at generation.

Finally, when incrementally generating a random word, the full prefix is used to extract next character. In usual languages such as English, knowing the full prefix is not necessary to generate a pronounceable word; instead, three or four characters are usually sufficient to choose a next character that will sound correctly. Restricting the generation of words based on a bounded prefix instead of the full word can be achieved by using the ``--prefix`` option of ``wagoner.word``. Similarly, the same option can be used on ``wagoner.table`` to directly generate (smaller) tables that will not propose next characters for longer prefixes.


Example
-------

Let's take the list of English words available on http://www-01.sil.org/linguistics/wordlists/english/. This list contains more than 100000 English words and should be useful to generate random words that sound English.

First thing to do before generating random words is to extract the table::

    python -m wagoner.table wordsEn.txt --output wordsEn.table

The table is extracted and saved in the ``wordsEn.table`` file. Then, we can generate random words::

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

You can see that some words are really like real words: ``crappinesa`` really looks like ``crappiness``, a word of ``wordsEn.txt``. To avoid generating such too real words, we can ask wagoner to only consider finite prefixes; this will avoid to be trapped in the increasing proability of ressembling the word ``crappiness`` as the word is generated::

    python -m wagoner.word wordsEn.table --prefix=4

that outputs, for example::

    rifiddlogi
    tionterehi
    zarintions
    pivermancu
    otintercen
    queraffeab
    hartniters
    yzebutshar
    utistrissi
    intimenpec

In this case, the words are still pronounceable, but are not words of the ``wordsEn.txt`` file.