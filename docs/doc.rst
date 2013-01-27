Author: Alberth
Date: Januari 2013

=====================
Design document EINTS
=====================

There are many NewGRF extensions for OpenTTD, and many of them contain text
strings to name items or to explain its mechanism.
All these text strings can be translated to different languages, to make the
NewGRF 'talk' to the user in his or her own language.

Currently, adding or changing text strings in translations is done in an
ad-hoc manner by exchanging files or patches through the forum or the issue
tracker.

An online translation web service could stream-line the process. The general
idea is that a NewGRF author uploads the text strings in one language, (the
base language), translators create text strings expressing the same notion in
a different language, and the NewGRF author downloads those translated text
strings, and adds them to the NewGRF file for distribution.

The number of text strings in a NewGRF varies, but typically, it is very
small. The largest amount of effort in creating a NewGRF goes into creating
the graphics and coding the behavior.
The number of NewGRFs produced by a single author is usually not very large,
as such it makes sense to share the online translation service between
different authors. For the translators, this can be useful in the sense that
it becomes easier to find what text strings (in various projects) need to be done.

Global requirements
-------------------

The translation web service should provide translation services to several
NewGRF projects. Each project has a set of text strings in a base language,
and aims to translate the text strings to one or more other languages.

Translators translate text strings in one or more NewGRF projects.
Text strings that exist in the base language, but not have no associated text
string in the translated language are said to be untranslated for that
language (this includes updating of existing text strings in the base
language).

Translators translate untranslated text strings into one of the languages they
know by creating a new text string in the language they translate to. The new
text string becomes associated with the text string in the base language.
Similarly, translators can improve existing translations by making a new text
string, and associating it with the same text string in the base language.

NewGRF authors want to get the best possible text strings to include in their
extension. For the base language, that is the newest version of each text
string in the base language. For translations, it is the newest text string in
the translated language associated with the text string in the base language,
if and only if they are valid. Text strings in the translation that are not
valid should not be considered. In that case, the conclusion is that there is
no translated text string in the language, and it is left empty. Normally, the
text string from the base language is used instead in such a case.


Languages and text strings
--------------------------

There is a set of supported languages by OpenTTD at the `NML reference site
<http://newgrf-specs.tt-wiki.net/wiki/NML:Language_files#LanguageIDs>`_
A language comes with its specific properties with respect to genders and
plural forms, which vary from language to language. Some languages also have
cases, where you can have several variants of one text string (for example, it
may depend on context which case of a text string should be used).
All NewGRF extensions use a subset of the above list of supported languages.

To make it easier to refer to a text string independent of language, each text
string has a name, called the *string name*.

A language has a text string for each of its cases, and one without case (the
*default text string*). Text strings often contain non-text items as well. The
list of `string codes
<http://newgrf-specs.tt-wiki.net/wiki/NML:Language_files#String_codes>`_ lists
codes that display non-text items. Text strings can also have `string
parameters
<http://newgrf-specs.tt-wiki.net/wiki/NML:Language_files#String_parameters>`_,
other pieces of text (like other strings or numbers) that are inserted in the
text string at the point of the parameter.

Defining and using genders is explained `at the NML reference site
<http://newgrf-specs.tt-wiki.net/wiki/NML:Language_files#Defining_genders>`_.
They are defined with the default text string, by prefixing the text string
with a ``{G=...}`` command. The gender of a string can be accessed and be used
to modify the text displayed to the user.

Plural forms work in much the same way, except the form to use is completely
decided by a numeric string parameter. Its use is explained at the `OpenTTD
language format wiki
<http://wiki.openttd.org/Format_of_langfiles#Plural_form>`_.

The biggest difference between both from a technical point of view, is that a
gender uses a string parameter *after* the ``{G ...}`` command, while a plural
``{P ...}`` uses a string parameter *before* it.

Valid text strings
------------------

The string parameters and the language properties make that not all text
strings are acceptable. We differentiate between correctness within a single
text string, correctness within a language, and correctness between languages
(or rather between a text string in the base language and in the translation).

A text string is valid when
- It only uses string codes and parameters from the above lists.
- It uses them in proper combinations (referencing the right kind of
  parameters).

A text string is valid in a language when
- It matches with the plural, gender, and cases of the language.

A text string is a valid translation when
- It has the same string parameters as the text string in the base language.
  There are some exceptions to this rule, eg ``{NBSP}`` does not need to be
  matched.



.. vim: tw=78 spell
