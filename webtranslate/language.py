"""
Languages in a project.
"""

class TextString:
    """
    Class for storing a text string. Objects are read-only in principle to allow sharing them
    between different languages.

    @ivar text: Text of the string.
    @type text: C{str}

    @ivar time_stamp: Time stamp associated with L{text}.
    @type time_stamp: L{Stamp}
    """
    def __init__(self, text, time_stamp):
        self.text = text
        self.time_stamp = time_stamp


class StringEntry:
    """
    Base class of a string.

    @ivar name: Name of the string.
    @type name: C{str}
    """
    def __init__(self, name):
        self.name = name

class TranslatedString(StringEntry):
    """
    String that is translated.

    - L{orig} or L{master} is non-empty, if they are both empty, there is no
      master string any more, and the string as a whole is obsolete.
    - If L{translation} is C{None}, there is no translated string.
      That also implies L{orig} is C{None}.
    - L{orig} may also be C{None} if the master string at the time cannot be recovered.
    - L{master} contains the current master text for this string.
      It is a newer string than the translation, the translation is C{None}, or
      the translation time stamp got changed without textual change iff L{orig}
      is not empty.

    @ivar text: Current text (the current translation).
    @type text: L{TextString} (C{None} if no translation exists)

    @ivar orig: Text of this string in the master language at the time L{text} was created.
    @type orig: L{TextString} (may be C{None})

    @ivar master: Current master text for this string.
    @type master: L{TextString} (may be C{None})
    """
    def __init__(self, name, text, orig, master):
        StringEntry.__init__(self, name)
        self.text = text
        self.orig = orig
        self.master = master



class MasterString(StringEntry):
    """
    String in a master language.

    @ivar name: Name of the string.
    @type name: C{str}

    @ivar master: Current master text.
    @type master: L{TextString}
    """
    # XXX Do we actually need this?
    def __init__(self, name, master):
        StringEntry.__init__(self, name)
        self.master = master


class Strings:
    """
    Wrapper class holding the strings of a language.

    @ivar texts: Strings in the language ordered by name of the string.
    @type texts: C{dict} of C{str} to L{MasterString} or of L{TranslatedString}
    """
    def __init__(self, texts):
        self.texts = texts


class Language:
    """
    A language.

    @ivar lang_file: Absolute path to the language filename.
    @type lang_file: C{str}

    @ivar lang_name: Language name.
    @type lang_name: C{str}

    @ivar master_lang: Language name of the master language, if available.
    @type master_lang: C{str} or C{None}

    @ivar strings: Strings in the language, if available.
    @type strings: L{Strings} or C{None}

    @ivar master_stamp: Last time stamp of its master language (if available).
    @type master_stamp: L{Stamp} or C{None}

    @ivar last_stamp: Last stamp of itself, if available.
    @type last_stamp: L{Stamp} or C{None}
    """
    # XXX Move last_stamp to L{Strings}
    def __init__(self, lang_file, lang_name, master_lang):
        self.lang_file = lang_file
        self.lang_name = lang_name
        self.master_lang = master_lang
        self.strings = None
        self.master_stamp = None
        self.last_stamp = None


class LanguageSystem:
    """
    The language system used by the project.

    @note: This class is the interface base class, derive a class from this one,
           and register it with L{language_systems}.
    """
    def get_name(self):
        """
        Retrieve the name of the language system.

        @return: The name of the language system.
        @rtype:  C{str}
        """
        raise NotImplementedError("Implement me in {}".format(type(self)))


class NewGrfLanguageSystem(LanguageSystem):
    """
    Language system for NewGRFs.
    """
    def get_name(self):
        return "newgrf"

# Mapping of name of the language system to its *class*.
language_systems = {'newgrf': NewGrfLanguageSystem}
