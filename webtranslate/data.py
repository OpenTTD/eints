"""
Project data.
"""
import time
from webtranslate import loader


class Project:
    """
    Project object.

    @ivar name: Project name.
    @type name: C{str}

    @ivar languages: Languages of the project ordered by name (iso_code).
    @type languages: C{dict} of C{str} to L{Language}

    @ivar base_language: Base language of the project.
    @type base_language: C{str} or C{None}

    @ivar skeleton: Skeleton of a language file, one tuple for each line.
    @type skeleton: C{list} of (C{str}, C{str}), where the first string is a type:
                    - 'literal'   Line literally copied
                    - 'string'    Line with a text string (possibly many when there are cases)
                    - 'grflangid' Line with the language id
                    - 'plural'    Plural number
                    - 'case'      Cases line
                    - 'gender'    Gender line
    """
    def __init__(self, name):
        self.name = name
        self.languages = {}
        self.base_language = None

        self.skeleton = []


class Language:
    """
    A language in a project.

    @ivar name: Name of the language.
    @type name: C{str}

    @ivar grflangid: Language id.
    @type grflangid: C{int}

    @ivar plural: Plural number of the language.
    @type plural: C{int}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language
    @type case: C{list} of C{str}

    @ivar changes: Changes to this language ordered by string name.
    @type changes: C{map} of C{str} to C{list} of L{Change}
    """
    def __init__(self, name):
        self.name = name
        self.grflangid = 0x7F
        self.plural = 1
        self.gender = []
        self.case  = []
        self.changes = {}


class Change:
    """
    A change (adding a new string in the base language, adding or updating a
    translation).

    @ivar string_name: String name of the string that was changed.
    @type string_name: C{str}

    @ivar case: Case of the string if available.
    @type case: C{str} or C{None}

    @ivar base_text: Used string in the base language.
    @type base_text: L{Text}

    @ivar new_text: Created string in the translated language (C{None} when
                    adding a new base language string).
    @type new_text: C{None} or L{Text}

    @ivar stamp: Time stamp of the change.
    @type stamp: L{Stamp}

    @ivar user: User making the change.
    @type user: L{User}
    """
    def __init__(self, string_name, case, base_text, new_text, stamp, user):
        self.string_name = string_name
        self.case = case
        self.base_text = base_text
        self.new_text = new_text
        self.stamp = stamp
        self.user = user


class Text:
    """
    Text of a string in a language.

    @ivar text: The actual text.
    @type text: C{str}

    @ivar case: Case of this string, if available.
    @type case: C{None} or C{str}

    @ivar stamp: Time stamp of creation of this text.
    @type stamp: L{Stamp}
    """
    def __init__(self, text, case, stamp):
        self.text = text
        self.case = case
        self.stamp = stamp


class Stamp:
    """
    Time stamp.

    @ivar seconds: Time in seconds since epoch.
    @type seconds: C{int}

    @ivar number: Index number, to allow more than one operation in a second.
    @type number: C{int}
    """
    def __init__(self, seconds, number):
        self.seconds = seconds
        self.number = number

last_stamp = 0 # A loooooong time ago.
last_index = -1

def make_stamp():
    """
    Construct a unique time stamp.

    @return: Unique time stamp.
    @rtype:  L{Stamp}
    """
    global last_stamp, last_index

    now = int(time.time())
    if now <= last_stamp:
        last_index = last_index + 1
        return Stamp(last_stamp, last_index)

    last_stamp = now
    last_index = 0
    return Stamp(last_stamp, last_index)


def load_project(fname):
    """
    Load the project xml data.

    @param fname: Name of the file to load.
    """
    data = loader.load_dom(fname)
    project = loader.get_single_child_node(data, 'project')

    proj_name = loader.collect_text_DOM(loader.get_single_child_node(project, 'name'))
    return Project(proj_name)
