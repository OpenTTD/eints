"""
Meta information about languages.
"""
import logging
import os
import re
import sys

from collections import namedtuple

log = logging.getLogger(__name__)

# Global variables initialized with L{set_all_languages}.
all_languages = None
grflangid = None
isocode = None


class PluralData:
    """
    @ivar plural: Plural form number.
    @type plural: C{int}

    @ivar count: Number of plural forms.
    @type count: C{int}

    @ivar description: Descriptio of plural forms.
    @type description: C{list} of C{str}
    """

    def __init__(self, plural, description):
        self.plural = plural
        self.description = description
        self.count = len(description)


all_plurals = {
    None: PluralData(None, []),
    0: PluralData(0, ["1", "other"]),
    1: PluralData(1, ["other"]),
    2: PluralData(2, ["0..1", "other"]),
    3: PluralData(3, ["1,21,31,...", "other", "0"]),
    4: PluralData(4, ["1", "2", "3..6", "7..10", "other"]),
    5: PluralData(5, ["1,21,31,...", "2..9,22..29,32..39,...", "other"]),
    6: PluralData(6, ["1,21,31,...", "2..4,22..24,32..34,...", "other"]),
    7: PluralData(7, ["1", "2..4,22..24,32..34,...", "other"]),
    8: PluralData(8, ["1,101,201,...", "2,102,202,...", "3..4,103..104,203..204,...", "other"]),
    9: PluralData(9, ["1,21,31,...", "other"]),
    10: PluralData(10, ["1", "2..4", "other"]),
    11: PluralData(11, ["yeong,il,sam,yuk,chil,pal", "i,sa,o,gu"]),
    12: PluralData(12, ["1", "0,2..10,102..110,202..210,...", "11..19,111..119,211..219,...", "other"]),
    13: PluralData(13, ["1,11", "2,12", "3..10,13..19", "other"]),
}


class LanguageData:
    """
    @ivar filename: Name of language file without extension.
    @type filename: C{str}

    @ivar name: Name of the language in English.
    @type name: C{str}

    @ivar ownname: Name of the language in the language itself.
    @type ownname: C{str}

    @ivar isocode: Systematic name of the language.
    @type isocode: C{str}

    @ivar plural: Plural form number.
    @type plural: C{int}

    @ivar grflangid: Language id according to the NewGRF system.
    @type grflangid: C{int}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language.
    @type case: C{list} of C{str}

    @ivar is_stable: Whether the language is considered to be 'stable'. Default C{True}.
    @type is_stable: C{bool}
    """

    def __init__(self, filename, found_lines):
        self.filename = filename
        self.name = found_lines["name"]
        self.ownname = found_lines["ownname"]
        self.isocode = found_lines["isocode"]
        self.plural = found_lines["plural"]
        self.grflangid = found_lines["grflangid"]

        gender = found_lines.get("gender")
        if gender is None:
            gender = []
        self.gender = gender

        case = found_lines.get("case")
        if case is None:
            case = []
        if "" not in case:
            case.append("")
        self.case = case
        self.is_stable = True  # By default, all languages are stable.


def as_str(text):
    return text.strip()


def as_int(text):
    if text[:2] in ("0x", "0X"):
        return int(text, base=16)
    else:
        return int(text, base=10)


def as_strlist(text):
    return list(set(text.split()))


# Recognized lines in a language file.
LanguageLine = namedtuple("LanguageLine", ["name", "pattern", "convert", "required"])
recognized = [
    LanguageLine("name", re.compile("##name +(.*) *$"), as_str, True),
    LanguageLine("ownname", re.compile("##ownname +(.*) *$"), as_str, True),
    LanguageLine("isocode", re.compile("##isocode +([a-z][a-z]_[A-Z][A-Z]) *$"), as_str, True),
    LanguageLine("plural", re.compile("##plural +((0[xX])?[0-9A-Fa-f]+) *$"), as_int, True),
    LanguageLine("grflangid", re.compile("##grflangid +((0[xX])?[0-9A-Fa-f]+) *$"), as_int, True),
    LanguageLine("gender", re.compile("##gender +(.*) *$"), as_strlist, False),
    LanguageLine("case", re.compile("##case +(.*) *$"), as_strlist, False),
]


def parse_file(fname):
    """
    Parse a language file, collecting the recognized lines.

    @param fname: Name of the file to read.
    @type  fname: C{str}

    @return: The found meta-information about a language.
    @rtype:  C{LanguageData}
    """
    handle = open(fname, "rt", encoding="utf-8")
    found_lines = {}
    for line in handle:
        if not line.startswith("##"):
            continue

        line = line.rstrip()
        for ll in recognized:
            m = ll.pattern.match(line)
            if m:
                found_lines[ll.name] = ll.convert(m.group(1))
                break

    handle.close()

    if not all(ll.name in found_lines for ll in recognized if ll.required):
        for ll in recognized:
            if ll.required and ll.name not in found_lines:
                log.error(
                    'File "%s" is missing required language line ##%s (or it has the wrong format)', fname, ll.name
                )
        sys.exit(1)

    return LanguageData(os.path.splitext(os.path.basename(fname))[0], found_lines)


def load_dir(directory):
    """
    Find all text files (".txt" extension) in the provided directory, and load
    the meta-language information from them.

    @param directory: Directory path containing language meta-data text files.
    @type  directory: C{str}

    @return: The found language information.
    @rtype:  C{list} of L{LanguageData}
    """
    result = []
    for fname in os.listdir(directory):
        if fname.lower().endswith(".txt"):
            result.append(parse_file(os.path.join(directory, fname)))

    return result


def set_all_languages(lang_infos):
    """
    Set the available language information.

    @param lang_infos: Language meta information to use.
    @type  lang_infos: C{list} of L{LanguageData}
    """
    global all_languages, grflangid, isocode

    all_languages = lang_infos

    grflangid = dict((x.grflangid, x) for x in all_languages)
    assert len(all_languages) == len(grflangid)

    isocode = dict((x.isocode, x) for x in all_languages)
    assert len(all_languages) == len(isocode)
