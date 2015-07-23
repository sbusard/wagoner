wagoner
=======

``wagoner`` is an anagram for rawogen, a random words generator.

``wagoner`` generates random words based on a given text. A random word is generated incrementally, and the given text is used to know which character should follow.


Usage
-----

``wagoner`` generates random words from tables extracted from texts. You need first to extract such a table from a text. To extract a table, use ``wagoner.table``::

    python3 -m wagoner.table TEXT --output text.table

This command will extract the table corresponding to ``TEXT`` into the file ``text.table``.

Then, given the extracted table, ``wagoner.word`` can extract random words::

    python3 -m wagoner.word text.table

This command will generate ten words of ten characters, based on the information in ``text.table``. To generate another number of words, use the ``--count`` option and to change their length, the ``--length`` option.