
.. contents::

=====================
Strings and languages
=====================

A large part of the application is about strings and languages, so it is
useful to explain a few things about them.

The basic idea of the application is that a (NewGRF or GameScript) project
provides a set of strings in some language (usually UK English). This language
is called *base language* of that project. The strings in the base language
are the central reference point.

All other languages (the *translation languages*) create the same set of
strings, by translating the text-part of each string into their own language.
Before explaining about strings however, it is useful to explain a few things
about languages first.

Languages
=========
What a language is exactly, is probably better left to Wikipedia. In this
document, only some technical properties of languages are explained, to make
the discussion about strings more understandable.

A language has

- a *name*. Actually, a language has several names. Eints uses a rather
  technical name ``<lang-name>_<region>``, where ``<lang-name>`` are two lower
  case letters and ``<region>`` are two upper case letters, for example
  ``en_GB`` for English spoken in Great Britain.
- a *grflangid*. A unique number known by the code, which serves as
  identification of a language in language files.
- a *pluralform*. Different languages use different ways to change words in
  the context of counts.
- optionally, *genders*. Depending on what you refer to, words may change.
  (For example '*his* books' versus '*her* books'.) Which genders exist changes
  with each language.
- optionally, *cases*. Depending on context, entire strings may be translated
  differently. NewGRFs allow to provide several text-parts for a string (one
  for each case).

Only the author of the code needs to know these things in detail. For everybody
else, the above list is just to get you familiar with some concepts that will be
needed when explaining strings (in a language).

Strings
=======

A single string has a unique *name* which serves as the
identification, and it has *text* which is the part that needs to be
translated.
For example::

        STR_EINTS     :Eints is a translator program.

The first word (``STR_EINTS``) is the name of this string, while all text
behind the colon is the text of the string (the colon itself is *not* part of
the text). The ``STR_`` prefix is not required, but is often added by
convention to distinguish the names from other name types.

The name-part stays the same for this string in every language (it may get a
case appended to it though, which will be explained later).
The text-part will usually change for each different language (but not always,
for example the above is a good text both in ``en_GB`` and in ``en_US``).


String commands
===============
If a string is just literal text like above, translating is relatively simple.
Just provide a text in a translation that expresses the same things as what
the string in the base language expresses.

Unfortunately, the text-parts often contain other things than just the text.
They are called *string commands*, and serve as place holder for
enhancing the layout, adding colour, and adding other pieces of text or
numbers.

There are two types of commands, *non-positional commands*, and *positional
commands*. Since the former type is the easiest to understand, they are
explained first.

A small sample of *non-positional commands* is shown below. (The full list can
be found at :ref:`string-commands-list`.) They are usually commands to display
symbols (like ©), or to change the colour of the text.

=============== ===========================================================
Command         Effect
=============== ===========================================================
``{}``          Continue at the next line
``{{}``         Output a ``{``
``{NBSP}``      Display a non-breaking space
``{COPYRIGHT}`` Display a copyright symbol
``{TRAIN}``     Display a train symbol
``{TINYFONT}``  Switch to a small font
``{BIGFONT}``   Switch to a big font
``{BLUE}``      Output following text in blue colour
``{SILVER}``    Output following text in silver colour
``{RED}``       Output following text in red colour
``{BLACK}``     Output following text in black colour
=============== ===========================================================

A string using the above commands can be::

        STR_EINTS     :{SILVER}Eints {BLACK}is a translator program.

This would display the word 'Eints' in a silver colour, and the other text in
black.

The second set of commands inserts numbers or other text into the string.
These commands are called *positional commands*. Below is a small sample (the
full list can be found at :ref:`string-commands-list`).

==================== ====== ====== =======================================
Command              Plural Gender Effect
==================== ====== ====== =======================================
``{COMMA}``           yes     no   Insert number into the text
``{STRING}``           no    yes   Insert a string into the text
``{CURRENCY}``         no     no   Insert an amount into the text
``{VELOCITY}``         no     no   Insert a speed into the text
==================== ====== ====== =======================================

A (not so good, but they'll get improved later) example::

        STR_BEER   :{COMMA} bottles of {STRING} are required

This string has two positional commands, namely ``{COMMA}`` at position ``0``
(counting starts from ``0``), and ``{STRING}`` at position ``1``.
These positions are important for the code that uses the ``STR_BEER`` string.
To display this string, it assumes that it must supply a number as parameter
``0``, and a text as parameter ``1``.
The latter is where *positional* comes from, it refers to the positions that
the code assumes for its parameters.
The *non-positional* is now also easy to understand. For those string
commands, the code does not need to supply anything, that is, it has no
parameter value for a colour switch like ``{GREEN}``.

The effect is that *non-positional* can be put anywhere without worrying about
parameter order (they have no parameter, so it cannot get confused about it),
while the *positional* commands must stay linked to the correct parameter or
weird things happen. The latter is done with a ``<postion>:`` prefix, as in::

        STR_BEER   :{0:COMMA} bottles of {1:STRING} are required

This is the same string as before, but now, the positions are explicitly
marked (with the ``0:`` and ``1:`` prefixes). With these prefixes, the system
will not get confused when you change the order of the positional commands, like::

        STR_BEER   :We need more {1:STRING}, get at least {0:COMMA} bottles!

(While this example is a little constructed, you can imagine that a translation
in a different language might need such swapping of positional commands to get
a good translation.)

Plural form
===========
As most of you have already seen, the example uses ``bottles``, that is, it
assumes that the program will never use the value ``1`` at position 0. If it
does, you'll get::

        1 bottles of wine are required

To fix this, the ``s`` needs to be optional in some way. This is where the
plural form comes in.
Basically, a plural form of a language looks at an numeric parameter, and
depending on the value and the language, it picks one of several texts to
display.

For example, English has a plural form with two texts, the first one in case
the number has the value 1, and the second one for all other values. For
example::

        STR_BEER   :{COMMA} {P "bottle" "bottles"} of {STRING} are required

The ``P`` means that a plural form must be selected. As expected it has two
texts, namely ``bottle`` (used for the value 1) and ``bottles`` (used for all
other numbers). The quotes ``"`` are not part of the text.
In case of a single (non-empty) word, the quotes can be omitted. The example can
thus also be written as ``{P bottle bottles}``.

The ``P`` command looks at the positional command just in front of it (ie the
``{COMMA}`` command). Like the positional commands you can also explicitly
state what parameter it should examine, by adding the position just behind the
``P``, as in ``{P 0 bottle bottles}``.
Last but not least, by convention the common part of both texts is normally
moved to before the command, as in ``bottle{P "" s}``. The ``bottle`` part is
now always displayed, and depending on the number either an empty word or the
'word' ``s`` gets added.

Gender
======
Gender works in much the same way as plurals, but they look at the gender
given with other strings. For example, in the English language::

        STR_MARY      :{G=f}Mary
        STR_JOHN      :{G=m}John

        STR_READ_BOOK :{STRING} reads his book

The first two strings ``STR_MARY`` and ``STR_JOHN`` define two persons. We
derive their gender from our general knowledge, but computers need to be
explicitly told the gender of a string. That's what the ``{G=f}`` and
``{G=m}`` is for. It says that the text ``Mary`` of ``STR_MARY`` is ``f`` in gender,
and the ``STR_JOHN`` text ``John`` is ``m`` in gender. The gender definition
itself is not part of the text.

The ``STR_READ_BOOK`` string has a string positional command ``{STRING}``. For
simplicity, let's assume that the code uses the ``STR_MARY`` or
``STR_JOHN`` strings at that position. So, the resulting strings are
``John reads his book`` and ``Mary reads his book``. Obviously the latter one
is incorrect, it should be ``her book``.

The gender selection command ``G`` can fix this.
In English, there are three genders, namely ``f``, ``m``, and ``n`` (female,
male, and neutral). The gender selection command ``G`` thus has three texts to
select from, as in::

        STR_READ_BOOK :{STRING} reads {G 0 her his its} book

The ``G`` command looks for a string behind it by default. The ``0`` in the
above example forces it to use the parameter at position ``0`` (that is, the
``{STRING}`` positional command).

Case
====

The English language does not have cases in the linguistic sense, which makes
explaining a little artificial. However, we can construct something similar.

Assume there are a bunch of locations::

        STR_ROOF             :on the roof
        STR_HOUSE            :in the house
        STR_SCHOOL           :at school

Using these locations one can express the location of a person::

        STR_LOCATION         :Peter is {STRING}
        STR_TRAVEL           :Peter goes {STRING}

Using these strings, the location of Peter can be expressed nicely,
and also where he is travelling to::

        Peter is on the roof
        Peter is in the house
        Peter is at school

        Peter goes on the roof
        Peter goes in the house
        Peter goes at school

Uh, oh... while the first three sentences are fine, the latter three
are wrong. The preposition does not only depend on the type of
the location, but also whether Peter is already there, or still travelling.

To fix this, we introduce a case ``target``::

        STR_ROOF             :on the roof
        STR_ROOF.target      :onto the roof
        STR_HOUSE            :in the house
        STR_HOUSE.target     :into the house
        STR_SCHOOL           :at school
        STR_SCHOOL.target    :to school

        STR_LOCATION         :Peter is {STRING}
        STR_TRAVEL           :Peter goes {STRING.target}

The ``{STRING.target}`` in this text states it prefers to have the ``target``
translation for the first string parameter. If the code uses ``STR_ROOF`` at
that position, the ``onto``-variant will be used instead of ``on``.
If a string does not have the desired case, the default case is used instead.

Now, ``STR_LOCATION`` can be used to state the location of Peter, and
``STR_TRAVEL`` can be used to express him travelling to a new location.
The location can in both cases be expressed with a single string id.
The usage of cases makes sure that the right preposition is used
in all cases.

.. vim: tw=78 spell
