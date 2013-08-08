
.. contents::

=====================
Strings and languages
=====================

A large part of the application is about strings and languages, so it is
useful to explain a few things about them.

The basic idea of the application is that a (NewGRF) project provides a set of
strings in some language (usually UK English). This language is called *base
language* of that project. The strings in the base language are the central reference point.

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
- a *grflangid*. A unique number known by NewGRFs, which serves as
  identification of a language in language files (used in NewGRF projects).
- a *pluralform*. Different languages use different ways to change words in
  the context of counts.
- optionally, *genders*. Depending on what you refer to, words may change.
  (For example '*his* books' versus '*her* books'.) Which genders exist changes
  with each language.
- optionally, *cases*. Depending on context, entire strings may be translated
  differently. NewGRFs allow to provide several text-parts for a string (one
  for each case).

Only the NewGRF author needs to know these things in detail. For everybody
else, the above list is just to get you familiar by some concepts that will be
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

To start slowly, a list of commands for enhancing layout and colour are
listed below. They are called *non-positional commands* for reasons that will
become clear later.

=============== ===========================================================
Command         Effect
=============== ===========================================================
``{}``          Continue at the next line
``{{}``         Output a ``{``
``{NBSP}``      Display a non-breaking space
``{COPYRIGHT}`` Display a copyright symbol
``{TRAIN}``     Display a train symbol
``{LORRY}``     Display a truck symbol
``{BUS}``       Display a bus symbol
``{PLANE}``     Display a plane symbol
``{SHIP}``      Display a ship symbol
``{TINYFONT}``  Switch to a small font
``{BIGFONT}``   Switch to a big font
``{BLUE}``      Output following text in blue colour
``{SILVER}``    Output following text in silver colour
``{GOLD}``      Output following text in gold colour
``{RED}``       Output following text in red colour
``{PURPLE}``    Output following text in purple colour
``{LTBROWN}``   Output following text in light brown colour
``{ORANGE}``    Output following text in orange colour
``{GREEN}``     Output following text in green colour
``{YELLOW}``    Output following text in yellow colour
``{DKGREEN}``   Output following text in dark green colour
``{CREAM}``     Output following text in cream colour
``{BROWN}``     Output following text in brown colour
``{WHITE}``     Output following text in white colour
``{LTBLUE}``    Output following text in light blue colour
``{GRAY}``      Output following text in gray colour
``{DKBLUE}``    Output following text in dark blue colour
``{BLACK}``     Output following text in black colour
=============== ===========================================================

A string using the above commands can be::

        STR_EINTS     :{SILVER}Eints {BLACK}is a translator program.

This would display the word 'Eints' in a silver colour, and the other text in
black.

A second set of commands inserts numbers or other text into the string.
These commands are called *positional commands*. Below is the list:

==================== ====== ====== =======================================
Command              Plural Gender Effect
==================== ====== ====== =======================================
``{COMMA}``           yes     no   Insert number into the text
``{SIGNED_WORD}``     yes     no   Insert number into the text
``{UNSIGNED_WORD}``   yes     no   Insert positive number into the text
``{HEX}``             yes     no   Insert hexadecimal number into the text
``{STRING}``           no    yes   Insert a string into the text
``{CURRENCY}``         no     no   Insert an amount into the text
``{VELOCITY}``         no     no   Insert a speed into the text
``{VOLUME}``           no     no   Insert a volume into the text
``{VOLUME_SHORT}``     no     no   Insert a volume into the text
``{POWER}``            no     no   Insert an horse-power into the text
``{WEIGHT}``           no     no   Insert a weight into the text
``{WEIGHT_SHORT}``     no     no   Insert a weight into the text
``{STATION}``          no     no   Insert a station name into the text
``{DATE1920_LONG}``    no     no   Insert a date into the text
``{DATE1920_SHORT}``   no     no   Insert a weight into the text
``{DATE_LONG}``        no     no   Insert a weight into the text
``{DATE_SHORT}``       no     no   Insert a weight into the text
``{POP_WORD}``         no     no   Insert nothing (and drop an argument)
==================== ====== ====== =======================================

An (not so good, but they'll get improved later) example::

        STR_BEER   :{COMMA} bottles of {STRING} are required

This string has two positional commands, namely ``{COMMA}`` at position ``0``
(counting starts from ``0``), and ``{STRING}`` at position ``1``.
These positions are important for the NewGRF. When it wants to display this
string, it assumes that it must supply a number as parameter ``0``, and a text as
parameter ``1``.
The latter is where *positional* comes from, it refers to the positions that
the NewGRF assumes for its parameters.
The *non-positional* is now also easy to understand. For those string
commands, the NewGRF does not need to supply anything, that is, it has no
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
In case of a single (non-empty) word, the quotes can be omitted.

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

        STR_MARY  :{G=f}Mary
        STR_JOHN  :{G=m}John

        STR_BOOKS :{STRING} his books

The first two strings ``STR_MARY`` and ``STR_JOHN`` define two persons. We
derive their gender from our general knowledge, but computers need to be
explicitly told the gender of a string. That's what the ``{G=f}`` and
``{G=m}`` is for. It says that the text ``Mary`` of ``STR_MARY`` is ``f`` in gender,
and the ``STR_JOHN`` text ``John`` is ``m`` in gender. The gender definition
itself is not part of the text.

The ``STR_BOOKS`` string has a string positional command ``{STRING}``. For
simplicity, let's assume that the NewGRF uses the ``STR_MARY`` or
``STR_JOHN`` strings at that position.
In English, there are three genders, namely ``f``, ``m``, and ``n`` (female,
male, and neutral). The gender selection command ``G`` thus has three texts to
select from, as in::

        STR_BOOKS :{STRING} {G 0 her his its} books

The ``G`` command looks for a string behind it by default. The ``0`` in the
above example forces it to use the parameter at position ``0`` (that is, the
``{STRING}`` positional command).

Case
====

The English language does not have cases, which makes explaining a little
artificial. For the purpose of discussing cases however, assume English has two
moods, a normal one, and a super-happy one, which are encoded as cases.

Cases can change wording in a very precise manner. Each string can be
translated for each case, and string replacements can give the preferred case.
An example::

        STR_OK      :ok
        STR_OK.fab  :super fabulous!

This defines the ``STR_OK`` string in two cases. The first line define the
default case, the second line defines the same string for the ``fab`` case.

The desired case of a string replacement can be specified too::

        STR_RESULT :The result is {STRING.fab}

The ``{STRING.fab}`` in this text states it prefers to have the ``fab``
translation for the first string parameter. If the NewGRF uses ``STR_OK`` at
that position, the ``super fabulous!`` text will be used.
If a string does not have the desired case, the default case is used instead.

.. vim: tw=78 spell
