"""
Project data.
"""
import calendar
import json
import logging
import re
import sys
import time

from xml.dom import minidom
from xml.dom.minidom import Node

from . import (
    loader,
    project_type,
)
from .newgrf import (
    language_file,
    language_info,
)

log = logging.getLogger(__name__)


def get_newest_change(chgs, case):
    """
    Get the newest change matching the case.

    @param chgs: Changes to select from.
    @type  chgs: C{list} of L{Change}

    @param case: Case to match.
    @type  case: C{str}

    @return: The newest change, if available.
    @rtype:  C{Change} or C{None}
    """
    best = None
    if chgs is not None:
        for chg in chgs:
            if chg.case != case:
                continue
            if best is None or best.stamp < chg.stamp:
                best = chg

    return best


def get_all_changes(chgs, cases, bchg):
    """
    Get all changes ordered by case and time.

    @param chgs: Changes to select from.
    @type  chgs: C{list} of L{Change} (C{None} is also accepted)

    @param cases: Available cases.
    @type  cases: C{list} of C{str}

    @param bchg: If given, change must be relative to this base change.
    @type  bchg: C{None} or L{Change}

    @return: Changes for each case, sorted from old to new.
    @rtype:  C{dict} of C{str} to C{list} of L{Change}
    """
    cases = dict((c, []) for c in cases)

    if chgs is not None:
        for chg in chgs:
            if bchg is not None and chg.base_text != bchg.base_text:
                continue
            clist = cases.get(chg.case)
            if clist is not None:
                clist.append(chg)

    for clist in cases.values():
        clist.sort()

    return cases


def get_all_newest_changes(chgs, cases):
    """
    Get the newest changes for all cases.

    @param chgs: Changes to select from.
    @type  chgs: C{list} of L{Change}

    @param cases: Available cases.
    @type  cases: C{list} of C{str}

    @return: Newest change for each case (for as far as it exists in the given L{chgs}).
    @rtype:  C{dict} of C{str} to (L{Change} or C{None})
    """
    cases = dict((c, None) for c in cases)
    cases[""] = None

    for chg in chgs:
        if chg.case in cases:
            if cases[chg.case] is None or cases[chg.case].stamp < chg.stamp:
                cases[chg.case] = chg
    return cases


class StatusDefinition:
    """
    Description of a string status.

    @ivar code: Numeric code of the string status.
    @type code: C{int}

    @ivar name: One-word name of the status.
    @type name: C{str}

    @ivar description: Description of the string status definition.
    @type description: C{str}

    @ivar baselng: Whether the status exists for base languages.
    @type baselng: C{bool}
    """

    def __init__(self, code, name, description, baselng):
        self.code = code
        self.name = name
        self.description = description
        self.baselng = baselng


MISSING_OK = 0  # String is missing, but that's allowed (non-default case string).
UNKNOWN = 1  # String has unknown state.
UP_TO_DATE = 2  # String is newer than the base string.
OUT_OF_DATE = 3  # String is older than the base string.
INVALID = 4  # String is invalid relative to the base string.
MISSING = 5  # The default case string is missing.

MAX_STATE = 6

STATUSES = [
    StatusDefinition(MISSING_OK, "Omitted", "The case was not needed in the translation", True),
    StatusDefinition(UNKNOWN, "Unknown", "The state of the translation was not decidable", False),
    StatusDefinition(UP_TO_DATE, "Correct", "The string is technically correct and up to date", True),
    StatusDefinition(
        OUT_OF_DATE,
        "Outdated",
        "A valid translation exists, but it needs review as a newer base language text is available",
        False,
    ),
    StatusDefinition(
        INVALID, "Invalid", "A translation exists, but its string parameters do not match with the base language", True
    ),
    StatusDefinition(MISSING, "Missing", "No translation could be found", False),
]

STATE_MAP = dict((sd.code, sd) for sd in STATUSES)

STATE_DISPLAY = [STATE_MAP[s] for s in [MISSING, INVALID, OUT_OF_DATE, UNKNOWN, UP_TO_DATE]]


def decide_all_string_status(projtype, base_chg, lng_chgs, lng, binfo):
    """
    Decide the state of all the cases of the string based on the information of L{base_chg} and
    the L{lng_chgs}.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param base_chg: Newest version of the string in the base language.
    @type  base_chg: L{Change}

    @param lng_chgs: Newest version of the string in the translation, for all cases.
    @type  lng_chgs: C{dict} of C{str} to (L{Change} or C{None})

    @param lng: Language.
    @type  lng: L{Language}

    @param binfo: String information of the base language (obtained from L{get_base_string_info}).
    @type  binfo: L{StringInfo}

    @return: Info about each case of the string in the translation, mapping of case to state value,
             and a list of found errors.
    @rtype:  C{dict} of C{str} to C{tuple} (C{int}, C{list} of L{ErrorMessage})
    """
    base_text = base_chg.base_text

    results = {}
    for case, chg in lng_chgs.items():
        if not projtype.allow_case and case != "":
            continue
        results[case] = get_string_status(projtype, chg, case, lng, base_text, binfo)
    return results


def get_string_status(projtype, lchg, case, lng, btext, binfo):
    """
    Get the status of a language string. Also collect its errors.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param lchg: Translation language change to examine.
    @type  lchg: L{Change} or C{None}

    @param case: Case of the change.
    @type  case: C{str}

    @param lng: Language.
    @type  lng: L{Language}

    @param btext: Current base text (may be different than C{lchg.base_text})
    @type  btext: C{Text}

    @param binfo: String information of the base language (obtained from L{get_base_string_info}).
    @type  binfo: L{StringInfo}

    @return: State of the translated string and any errors.
    @rtype:  C{tuple} (C{int}, C{list} of L{ErrorMessage})
    """
    if case == "":
        if lchg is None:
            return MISSING, []
    elif lchg is None or lchg.new_text.text == "":
        return MISSING_OK, []

    if lchg.base_text != btext or lchg.stamp < btext.stamp:
        state = OUT_OF_DATE
    else:
        state = UP_TO_DATE

    assert projtype.allow_case or lchg.case == ""
    linfo = language_file.check_string(projtype, lchg.new_text.text, lchg.case == "", binfo.extra_commands, lng, False)
    if not language_file.compare_info(projtype, binfo, linfo):
        state = INVALID

    return state, linfo.errors


def convert_num(txt, default):
    """
    Convert the number given in L{txt} to a numeric form.

    @param txt: Text containing the number.
    @type  txt: C{str} or C{None}

    @param default: Default value, in case the L{txt} is not a number.
    @type  default: C{int} or C{None}

    @return: The numeric value of the number if it is convertible.
    @rtype:  C{int} or the provided default
    """
    if txt is None:
        return default
    m = re.match("\\d+$", txt)
    if not m:
        return default
    return int(txt, 10)


class XmlLoader:
    """
    Helper class to load a project from an XML file.

    @ivar stamps: Time stamps loaded so far, mapping of seconds and indices to L{Stamp}.
    @type stamps: C{dict} of (C{int}, C{int}) to L{Stamp}

    @ivar texts: Loaded texts, ordered by their reference.
    @type texts: C{dict} of C{str} to L{Text}

    @ivar split_languages: If set, don't expect the languages to be part of the project.
                           They have been saved separately.
    @type split_languages: C{bool}
    """

    def __init__(self, split_languages):
        self.stamps = {}
        self.texts = {}
        self.split_languages = split_languages

    def get_stamp(self, secs, index):
        """
        Get a time stamp from loaded 'stamp' data.

        @param secs: Seconds since epoch.
        @type  secs: C{int}

        @param index: Index within L{secs}.
        @type  index: C{int}

        @return: Associated time stamp.
        @rtype:  L{Stamp}
        """
        global last_stamp, last_index

        s = self.stamps.get((secs, index))
        if s is None:
            s = Stamp(secs, index)
            self.stamps[(secs, index)] = s
            if last_stamp < secs:
                last_stamp = secs
                last_index = index
            elif last_stamp == secs and last_index < index:
                last_index = index

        return s

    def load_project(self, fname):
        """
        Load a project from the given file.

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @return: The loaded project. Depending on L{split_languages} set during construction of the
                 object, the project may not have all languages.
        @rtype:  L{Project}
        """
        data = loader.load_dom(fname)
        pnode = loader.get_single_child_node(data, "project")
        self.stamps = {}

        # Load texts. If cases are not allowed, loading the texts from here is no problem, as they are
        # discarded after loading the change.
        self.texts = {}
        texts = loader.get_single_child_node(pnode, "texts", True)
        if texts is not None:
            for node in loader.get_child_nodes(texts, "string"):
                ref = node.getAttribute("ref")
                self.texts[ref] = get_text_node(self, node)

        return load_project(self, pnode)

    def load_language(self, projtype, fname):
        """
        Load a language into the project from the give filename.

        @param projtype: Project type.
        @type  projtype: L{ProjectType}

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @return: The loaded language.
        @rtype:  L{Language}
        """
        data = loader.load_dom(fname)
        pnode = loader.get_single_child_node(data, "language")
        self.stamps = {}

        # Load texts. If cases are not allowed, loading the texts from here is no problem, as they are
        # discarded after loading the change.
        self.texts = {}
        texts = loader.get_single_child_node(pnode, "texts", True)
        if texts is not None:
            for node in loader.get_child_nodes(texts, "string"):
                ref = node.getAttribute("ref")
                self.texts[ref] = get_text_node(self, node)

        return load_language(self, projtype, pnode)

    def get_textref(self, ref):
        """
        Get the text object associated with the L{ref} string.

        @param ref: Reference name of the text.
        @type  ref: C{str}

        @return: The text object belonging to the reference.
        @rtype:  L{Text}
        """
        return self.texts[ref]


class JsonLoader:
    """
    Helper class to load a project from a Json file.

    @ivar split_languages: If set, don't expect the languages to be part of the project.
                           They have been saved separately.
    @type split_languages: C{bool}
    """

    def __init__(self, split_languages):
        self.split_languages = split_languages

    def load_project(self, fname):
        """
        Load a project from the given file.

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @return: The loaded project. Depending on L{split_languages} set during construction of the
                 object, the project may not have all languages.
        @rtype:  L{Project}
        """
        handle = open(fname, "rt", encoding="utf-8")
        data = json.load(handle)
        handle.close()
        return load_project_json(self, data)

    def load_language(self, projtype, fname):
        """
        Load a language into the project from the give filename.

        @param projtype: Project type.
        @type  projtype: L{ProjectType}

        @param fname: Name of the file to load.
        @type  fname: C{str}

        @return: The loaded language.
        @rtype:  L{Language}
        """
        handle = open(fname, "rt", encoding="utf-8")
        data = json.load(handle)
        handle.close()
        return load_language_json(projtype, data)


class XmlSaver:
    """
    Saver helper class, storing the top-level document, and the referenced texts.

    @ivar doc: Xml document node.
    @type doc: L{xml.dom.minidom.Document}

    @ivar texts_node: Node containing the texts.
    @type texts_node: L{xml.dom.minidom.Node}

    @ivar texts: Text references of the project, ordered by text object.
    @type texts: C{dict} of L{Text} to C{str}

    @ivar split_languages: If set, don't save the languages as part of the project. They are
                           saved separately at a later stage.
    @type split_languages: C{bool}

    @param share_text: Whether to share text strings with a 'text' node.
    @type  share_text: C{bool}

    @ivar number: Number for creating unique text references.
    @type number: C{int}
    """

    def __init__(self, split_languages, share_text):
        self.doc = None
        self.texts_node = None
        self.texts = {}
        self.split_languages = split_languages
        self.share_text = share_text
        self.number = 1

    def save_project(self, project, fname):
        """
        Save a project as an xml doc document.

        @param project: Project to save.
        @type  project: L{Project}

        @param fname: Name of the file to write.
        @type  fname: C{str}
        """
        self.doc = minidom.Document()
        if self.share_text:
            self.texts_node = self.doc.createElement("texts")
            self.texts = {}
            self.number = 1

        node = save_project(self, project)
        if self.share_text and len(self.texts) > 0:
            node.appendChild(self.texts_node)

        self.doc.appendChild(node)
        handle = open(fname, "w", encoding="utf-8")
        handle.write(self.doc.toprettyxml())
        handle.close()

    def save_language(self, projtype, lng, fname):
        """
        Save a language as xml document.

        @param projtype: Project type.
        @type  projtype: L{ProjectType}

        @param lng: Language to save.
        @type  lng: L{Language}

        @param fname: Name of the file to write.
        @type  fname: C{str}
        """
        assert self.split_languages

        self.doc = minidom.Document()
        if self.share_text:
            self.texts_node = self.doc.createElement("texts")
            self.texts = {}
            self.number = 1

        node = save_language(self, projtype, lng)
        if self.share_text and len(self.texts) > 0:
            node.appendChild(self.texts_node)

        self.doc.appendChild(node)
        handle = open(fname, "w", encoding="utf-8")
        handle.write(self.doc.toprettyxml())
        handle.close()

    def get_textref(self, text):
        """
        Construct a node containing the text, and return a reference to it.

        @param text: Text to save.
        @type  text: L{Text}

        @return: Reference to the text node.
        @rtype:  C{str}
        """
        assert self.share_text

        ref = self.texts.get(text)
        if ref is not None:
            return ref

        node, ref = make_text_node(self, text, "string", self.number)
        self.number = self.number + 1

        self.texts_node.appendChild(node)
        self.texts[text] = ref
        return ref


class JsonSaver:
    """
    Saver helper class.

    @ivar split_languages: If set, don't save the languages as part of the project. They are
                           saved separately at a later stage.
    @type split_languages: C{bool}
    """

    def __init__(self, split_languages):
        self.split_languages = split_languages

    def save_project(self, project, fname):
        """
        Save a project as an xml doc document.

        @param project: Project to save.
        @type  project: L{Project}

        @param fname: Name of the file to write.
        @type  fname: C{str}
        """
        node = save_project_json(self, project)
        handle = open(fname, "wt", encoding="utf-8")
        json.dump(node, handle)
        handle.close()

    def save_language(self, projtype, lng, fname):
        """
        Save a language as xml document.

        @param projtype: Project type.
        @type  projtype: L{ProjectType}

        @param lng: Language to save.
        @type  lng: L{Language}

        @param fname: Name of the file to write.
        @type  fname: C{str}
        """
        assert self.split_languages

        node = save_language_json(projtype, lng)
        handle = open(fname, "wt", encoding="utf-8")
        json.dump(node, handle)
        handle.close()


class Project:
    """
    Project object.

    @ivar human_name: Project name for humans.
    @type human_name: C{str}

    @ivar projtype: Project type.
    @type projtype: L{ProjectType}

    @ivar url: URL to Project Home Page (somewhere on the internet).
    @type url: C{str}

    @ivar statistics: Statistics for all strings in all languages. Managed by the project
                      meta-data, not stored in the project.
                      Mapping of language name to string name to list of case and state, where
                      the state is UP_TO_DATE, OUT_OF_DATE, INVALID, MISSING_OK, or MISSING.
    @type statistics: C{dict} of C{str} to C{dict} of C{str} to C{list} of (C{str}, C{int})

    @ivar languages: Languages of the project ordered by name (isocode).
    @type languages: C{dict} of C{str} to L{Language}

    @ivar base_language: Base language of the project.
    @type base_language: C{str} or C{None}

    @ivar modified: Whether the project object (excluding the languages) has been modified
                    (and needs writing to disk).
    @type modified: C{bool}

    @ivar normalized: Computed current base language words ordered by string name. Used to get
                      related strings. (Created as a side-effect of setting up L{word_scores}.)
    @type normalized: C{dict} of C{str} to C{list} of C{str}

    @ivar word_scores: Computed mapping of string scores ordered by word. Built on demand by
                       L{build_related_string_map}.
    @type word_scores: C{dict} of C{str} to a C{dict} of C{str} to C{float}, or C{None}

    @ivar skeleton: Skeleton of a language file, one tuple for each line.
    @type skeleton: C{list} of (C{str}, C{str}), where the first string is a type:
                    - 'literal'   Line literally copied
                    - 'string'    Column with ':', and line with a text string
                                  (possibly many when there are cases)
                    - 'grflangid' Line with the language id
                    - 'plural'    Plural number
                    - 'case'      Cases line
                    - 'gender'    Gender line
                    - 'pragma'    Custom pragma with specific name
    """

    def __init__(self, human_name, projtype, url=""):
        self.human_name = human_name
        self.projtype = projtype
        self.url = url
        self.statistics = {}
        self.languages = {}
        self.base_language = None
        self.modified = False
        self.normalized = None  # Created while creating 'word_scores'
        self.word_scores = None

        self.skeleton = []

    def set_modified(self):
        """
        Mark the project object (excluding the languages) as modified (and needs to be written to disk).
        """
        self.modified = True

    def get_base_language(self):
        """
        Get the base language of the project.

        @return: The base language of the project, if it exists.
        @rtype:  L{Language} or C{None}
        """
        if self.base_language is None:
            return None
        return self.languages.get(self.base_language)

    def flush_related_cache(self):
        """
        Delete the cache of related strings. Will be rebuild when needed.
        """
        self.normalized = None
        self.word_scores = None

    def build_related_string_map(self):
        """
        Build the L{word_scores} variable.
        """
        if self.word_scores is not None:
            return
        blng = self.get_base_language()
        if blng is None:
            return

        self.normalized = {}  # Mapping of string name to its words.
        for sname, chgs in blng.changes.items():
            chg = get_newest_change(chgs, "")
            assert chg is not None
            line = re.sub("{([^}]*)}", " ", chg.base_text.text)
            words = [word.lower() for word in re.split("\\W+", line) if len(word) > 3]
            if len(words) > 0:
                self.normalized[sname] = words

        self.word_scores = {}
        # For all words in each string, add the string to the word scores.
        for sname, words in self.normalized.items():
            for w in words:
                scores = self.word_scores.get(w)
                if scores is None:
                    scores = {}
                    self.word_scores[w] = scores
                scores[sname] = 1.0  # The string has this word.

        # To get rid of differences for singular vs plural forms, we also accept
        # substrings of a word too, but at a lower score (namely the fraction of matching).
        for w, scores in self.word_scores.items():
            for w2, scores2 in self.word_scores.items():
                if w != w2 and w in w2:
                    # Add the longer words to the short word with a fractional score.
                    for sname2 in scores2:
                        if sname2 not in scores:
                            scores[sname2] = len(w) / len(w2)

    def get_related_strings(self, sname):
        """
        Get the names of the related strings for string L{sname}.

        @param sname: Name of the string that needs related strings.
        @type  sname: C{str}

        @return: Related strings.
        @rtype:  C{list} of C{str}
        """
        self.build_related_string_map()
        if self.word_scores is None:
            return []

        words = self.normalized.get(sname)
        if words is None:
            return []

        strings = {}  # Mapping of other strings to cumulative score.
        for word in words:
            for sname2, score2 in self.word_scores[word].items():
                if sname != sname2:
                    val = strings.get(sname2, 0.0)
                    strings[sname2] = val + score2
        best = (None, 0.0)
        best = [best, best, best, best, best]
        for sname, score in strings.items():
            i = 5  # Position of the entry is 'i'
            while i > 0 and score > best[i - 1][1]:
                i = i - 1
            if i > 4:
                continue
            elif i == 4:
                best[4] = (sname, score)
            else:
                best = best[:i] + [(sname, score)] + best[i:-1]

        return [b[0] for b in best if b[0] is not None]

    def get_all_languages(self):
        """
        Get an iterator returning meta-data of all languages that may be used in the project.

        @return: Iterator returning language meta-data that could be used in the project.
        @rtype:  C{iter} of L{LanguageData}
        """
        return (linfo for linfo in language_info.all_languages if self.projtype.allow_language(linfo))


def load_project(xloader, node):
    """
    Load a project node from the Xml file.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Node containing the project.
    @type  node: L{xml.dom.minidom.Node}

    @return: The loaded project.
    @rtype:  L{Project}
    """
    assert node.tagName == "project"
    human_name = node.getAttribute("name")
    projtype = project_type.project_types[loader.get_opt_DOMattr(node, "projtype", "newgrf")]
    url = node.getAttribute("url")
    project = Project(human_name, projtype, url)

    project.languages = {}
    if not xloader.split_languages:
        langnodes = loader.get_child_nodes(node, "language")
        for lnode in langnodes:
            lng = load_language(xloader, projtype, lnode)
            project.languages[lng.name] = lng

    baselang = loader.get_opt_DOMattr(node, "baselang", None)

    if not xloader.split_languages:
        if baselang is None or baselang not in project.languages:
            if len(project.languages) > 0:
                log.warning('Project "%s" has no base language, dropping all translations', project.human_name)
                project.languages = {}
            project.base_language = None
            return project  # Also skip loading the skeleton.

    project.base_language = baselang
    project.flush_related_cache()

    skelnode = loader.get_single_child_node(node, "skeleton")
    if skelnode is None:
        project.skeleton = []
    else:
        project.skeleton = load_skeleton(xloader, skelnode)
    return project


def load_project_json(jloader, node):
    """
    Load the project from the Json format.

    @param jloader: Loader class.
    @type  jloader: L{JsonLoader}

    @param node: Node in Json format containing the project data.
    @type  node: C{dict}

    @return: The loaded project.
    @rtype:  L{Project}
    """
    assert node["project_version"] == 1
    human_name = node["name"]
    projtype = project_type.project_types[node["projtype"]]
    url = node["url"]
    project = Project(human_name, projtype, url)

    project.languages = {}
    if not jloader.split_languages:
        langnodes = node["languages"]
        for lnode in langnodes:
            lng = load_language_json(projtype, lnode)
            project.languages[lng.name] = lng

    baselang = node["baselang"]

    if not jloader.split_languages:
        if baselang is None or baselang not in project.languages:
            if len(project.languages) > 0:
                log.warning('Project "%s" has no base language, dropping all translations', project.human_name)
                project.languages = {}
            project.base_language = None
            return project  # Also skip loading the skeleton.

    project.base_language = baselang
    project.flush_related_cache()
    project.skeleton = load_skeleton_json(node["skeleton"])
    return project


def load_skeleton(xloader, node):
    """
    Load the skeleton list from the xml node.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Skeleton root node.
    @type  node: L{xml.dom.minidom.Node}

    @return: The loaded skeleton data, as described in the L{Project} class.
    @rtype:  C{list} of (C{str}, C{str})
    """
    assert node.tagName == "skeleton"
    skeleton = []
    for lnode in node.childNodes:
        if lnode.nodeType != Node.ELEMENT_NODE:
            continue
        if lnode.tagName == "literal":
            text = loader.collect_text_DOM(lnode)
            skeleton.append(("literal", text))
        elif lnode.tagName == "string":
            column = convert_num(loader.get_opt_DOMattr(lnode, "column", "40"), 40)
            name = lnode.getAttribute("name")
            if name is not None:
                skeleton.append(("string", (column, name)))
        elif lnode.tagName == "pragma":
            name = lnode.getAttribute("name")
            skeleton.append(("pragma", name))
        elif lnode.tagName in ("grflangid", "plural", "case", "gender"):
            skeleton.append((lnode.tagName, ""))
    return skeleton


def save_project(xsaver, proj):
    """
    Save the project to Xml.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param proj: Project to save.
    @type  proj: L{Project}

    @return: Node containing the project.
    @rtype:  L{xml.dom.minidom.Node}
    """
    node = xsaver.doc.createElement("project")
    node.setAttribute("name", proj.human_name)
    node.setAttribute("projtype", proj.projtype.name)
    node.setAttribute("url", proj.url)
    blng = proj.get_base_language()
    if blng is not None:
        node.setAttribute("baselang", blng.name)

    # Save languages in alphabetical order
    if not xsaver.split_languages:
        langs = list(proj.languages.items())
        langs.sort()
        for lang in langs:
            lnode = save_language(xsaver, proj.projtype, lang[1])
            node.appendChild(lnode)

    skelnode = save_skeleton(xsaver, proj.skeleton)
    node.appendChild(skelnode)
    return node


def save_project_json(jsaver, proj):
    """
    Save the project in Json.

    @param jsaver: Saver class.
    @type  jsaver: L{JsonSaver}

    @return: Node containing the project.
    @rtype:  C{dict}
    """
    result = {}
    result["project_version"] = 1
    result["name"] = proj.human_name
    result["projtype"] = proj.projtype.name
    result["url"] = proj.url

    blng = proj.get_base_language()
    if blng is not None:
        blng = blng.name
    result["baselang"] = blng

    if not jsaver.split_languages:
        languages = []
        langs = list(proj.languages.items())
        langs.sort()
        for lang in langs:
            languages.append(save_language_json(proj.projtype, lang[1]))
        result["languages"] = languages

    result["skeleton"] = save_skeleton_json(proj.skeleton)
    return result


def save_skeleton(xsaver, skel):
    """
    Save the skeleton list.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param skel: Skeleton list, as described in the L{Project} class.
    @type  skel: C{list} of (C{str}, C{str})

    @return: The skeleton data as xml node.
    @rtype:  L{xml.dom.minidom.Node}
    """
    root = xsaver.doc.createElement("skeleton")
    for stp, sparm in skel:
        node = xsaver.doc.createElement(stp)
        if stp == "literal" and len(sparm) > 0:
            txt = xsaver.doc.createTextNode(sparm)
            node.appendChild(txt)
        elif stp == "string":
            column, sname = sparm
            node.setAttribute("name", sname)
            node.setAttribute("column", str(column))
        elif stp == "pragma":
            node.setAttribute("name", sparm)

        root.appendChild(node)
    return root


def save_skeleton_json(skel):
    """
    Save skeleton file in Json format.

    @param skel: Skeleton list, as described in the L{Project} class.
    @type  skel: C{list} of (C{str}, C{str})

    @return: Skeleton file in Json format.
    @rtype:  List of lines.
    """
    result = []
    for stp, sparm in skel:
        if stp in ("literal", "pragma", "grflangid", "plural", "case", "gender"):
            result.append([stp, sparm])
        elif stp == "string":
            column, sname = sparm
            result.append([stp, column, sname])

    return result


def load_skeleton_json(node):
    """
    Load skeleton file from the Json node.

    @param node: The node with the saved skeleton data in Json format.
    @type  node: C{list}

    @return: The loaded skeleton data, as described in the L{Project} class.
    @rtype:  C{list} of (C{str}, C{str})
    """
    skeleton = []
    for line in node:
        if line[0] in ("literal", "pragma", "grflangid", "plural", "case", "gender"):
            skeleton.append((line[0], line[1]))
        elif line[0] == "string":
            skeleton.append((line[0], (line[1], line[2])))

    return skeleton


class Language:
    """
    A language in a project.

    @ivar name: Name of the language (isocode).
    @type name: C{str}

    @ivar info: Vanilla language info. The actually used plurals/genders/cases may differ.
    @type info: L{LanguageData}

    @ivar custom_pragmas: Custom pragmas, which are preserved when uploading languages.
    @type custom_pragmas: C{dict} of C{str} to C{str}

    @ivar grflangid: Language id.
    @type grflangid: C{int}

    @ivar plural: Plural number of the language, if specified.
    @type plural: C{int} or C{None}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language (sorted).
    @type case: C{list} of C{str}

    @ivar modified: Whether the language strings have been modified in some way (and need to be written out).
    @type modified: C{bool}

    @ivar changes: Changes to this language ordered by string name, for strings
                   that exist in the language.
    @type changes: C{map} of C{str} to (C{list} of L{Change} or C{None})

    @note: L{case} is sorted to make 'download language' output the default case first,
           which makes NML more happy.
    """

    def __init__(self, name):
        self.name = name
        self.info = language_info.isocode.get(name)
        self.custom_pragmas = {}
        self.grflangid = 0x7F
        self.plural = None
        self.gender = []
        self.case = [""]
        self.modified = False
        self.changes = {}

    def set_modified(self):
        """
        Mark the language as modified (and needs to be written to disk).
        """
        self.modified = True


def save_language(xsaver, projtype, lang):
    """
    Save the language to Xml.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param lang: Language to save.
    @type  lang: L{Language}

    @return: Node containing the language.
    @rtype:  L{xml.dom.minidom.Node}
    """
    # Paranoia check, genders and cases should not have white space in them.
    for g in lang.gender:
        assert " " not in g
    for c in lang.case:
        assert " " not in c

    node = xsaver.doc.createElement("language")
    node.setAttribute("name", lang.name)
    node.setAttribute("langid", str(lang.grflangid))
    if lang.plural is not None:
        node.setAttribute("plural", str(lang.plural))
    if projtype.allow_gender and len(lang.gender) > 0:
        node.setAttribute("gender", " ".join(lang.gender))
    cases = [c for c in lang.case if c != ""]
    if len(cases) > 0:
        node.setAttribute("cases", " ".join(cases))

    # Sort the custom pragmas.
    custom_pragmas = list(lang.custom_pragmas.items())
    custom_pragmas.sort()
    for pname, pvalue in custom_pragmas:
        pragma_node = xsaver.doc.createElement("pragma")
        pragma_node.setAttribute("name", pname)
        pragma_node.appendChild(xsaver.doc.createTextNode(pvalue))
        node.appendChild(pragma_node)

    # Sort the strings of the language.
    changes = list(lang.changes.items())
    changes.sort()
    for chgs in changes:
        chgs[1].sort()  # Sort changes
        for chg in chgs[1]:
            cnode = save_change(xsaver, projtype, chg)
            if cnode is not None:
                node.appendChild(cnode)
    return node


def save_language_json(projtype, lang):
    """
    Save the language to Json.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param lang: Language to save.
    @type  lang: L{Language}

    @return: Node containing the language.
    @rtype:  C{dict}
    """
    result = {}
    result["language_version"] = 1
    result["name"] = lang.name
    result["grflangid"] = lang.grflangid
    result["plural"] = lang.plural

    if projtype.allow_gender and len(lang.gender) > 0:
        result["gender"] = " ".join(lang.gender)

    cases = [c for c in lang.case if c != ""]
    if len(cases) > 0:
        result["cases"] = " ".join(cases)

    custom_pragmas = list(lang.custom_pragmas.items())
    custom_pragmas.sort()
    result["pragma"] = custom_pragmas

    res_changes = []
    changes = list(lang.changes.items())
    changes.sort()
    for chgs in changes:
        chgs[1].sort()  # Sort changes
        for chg in chgs[1]:
            cnode = save_change_json(projtype, chg)
            if cnode is not None:
                res_changes.append(cnode)
    result["change"] = res_changes
    return result


def load_language(xloader, projtype, node):
    """
    Load a language from the given xml node.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param node: Node containing the language.
    @type  node: L{xml.dom.minidom.Node}

    @return: The loaded language.
    @rtype:  L{Language}
    """
    assert node.tagName == "language"
    name = node.getAttribute("name")

    lng = Language(name)
    lng.grflangid = int(node.getAttribute("langid"), 10)
    plural = loader.get_opt_DOMattr(node, "plural", None)
    if plural is not None:
        lng.plural = int(plural, 10)
    else:
        lng.plural = lng.info.plural

    gender = loader.get_opt_DOMattr(node, "gender", None)
    if not projtype.allow_gender:
        lng.gender = []
    elif gender is not None:
        lng.gender = gender.split(" ")
    else:
        lng.gender = lng.info.gender

    case = loader.get_opt_DOMattr(node, "cases", None)
    if not projtype.allow_case or case == "":
        lng.case = [""]
    elif case is not None:
        lng.case = [""] + case.split(" ")
    else:
        lng.case = lng.info.case

    lng.custom_pragmas = {}
    for pragma_node in loader.get_child_nodes(node, "pragma"):
        pname = pragma_node.getAttribute("name")
        pvalue = loader.collect_text_DOM(pragma_node)
        pvalue = language_file.sanitize_text(pvalue)
        lng.custom_pragmas[pname] = pvalue

    lng.changes = {}
    for ch_node in loader.get_child_nodes(node, "change"):
        change = load_change(xloader, ch_node)
        if not projtype.allow_case and change.case != "":
            continue
        chgs = lng.changes.get(change.string_name)
        if chgs is None:
            lng.changes[change.string_name] = [change]
        else:
            chgs.append(change)

    return lng


def load_language_json(projtype, node):
    """
    Load a language from the given Json node.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param node: Node containing the language.
    @type  node: C{dict}

    @return: The loaded language.
    @rtype:  L{Language}
    """
    assert "language_version" in node
    assert node["language_version"] == 1

    lng = Language(node["name"])

    assert isinstance(node["grflangid"], int)
    lng.grflangid = node["grflangid"]

    assert node["plural"] is None or isinstance(node["plural"], int)
    lng.plural = node["plural"]
    if lng.plural is None:
        lng.plural = lng.info.plural

    if not projtype.allow_gender:
        lng.gender = []
    elif "gender" in node:
        lng.gender = node["gender"].split(" ")
    else:
        lng.gender = lng.info.gender

    case = node.get("cases")
    if not projtype.allow_case or case == "":
        lng.case = [""]
    elif case is not None:
        lng.case = [""] + case.split(" ")
    else:
        lng.case = lng.info.case

    assert isinstance(node["pragma"], list)
    lng.custom_pragmas = dict(node["pragma"])

    lng.changes = {}
    for ch_node in node["change"]:
        change = load_change_json(ch_node)
        if not projtype.allow_case and change.case != "":
            continue
        chgs = lng.changes.get(change.string_name)
        if chgs is None:
            lng.changes[change.string_name] = [change]
        else:
            chgs.append(change)

    return lng


class Change:
    """
    A change (adding a new string in the base language, adding or updating a
    translation).

    @ivar string_name: String name of the string that was changed.
    @type string_name: C{str}

    @ivar case: Case of the string.
    @type case: C{str}

    @ivar base_text: Used string in the base language.
    @type base_text: L{Text}

    @ivar new_text: Created string in the translated language (C{None} when
                    adding a new base language string).
    @type new_text: C{None} or L{Text}

    @ivar stamp: Time stamp of the change.
    @type stamp: L{Stamp}

    @ivar user: User making the change, if known.
    @type user: C{str} or C{None}

    @ivar last_upload: This change was the last uploaded text (L{base_text} for
                       the base language, and L{new_text} for the translations).
    @type last_upload: C{bool}

    @note: There is at most one L{last_upload} change for each string in each language.
    """

    __slots__ = ("string_name", "case", "base_text", "new_text", "stamp", "user", "last_upload")

    def __init__(self, string_name, case, base_text, new_text, stamp, user, last_upload=False):
        assert string_name is not None
        self.string_name = sys.intern(string_name)
        self.case = sys.intern(case)
        self.base_text = base_text
        self.new_text = new_text
        self.stamp = stamp
        self.user = sys.intern(user)
        self.last_upload = last_upload

    def __str__(self):
        return "Change('{}', base={}, new={})".format(self.string_name, str(self.base_text), str(self.new_text))

    def __lt__(self, other):
        if not isinstance(other, Change):
            return
        return self.stamp < other.stamp

    def __eq__(self, other):
        if not isinstance(other, Change):
            return
        return self.stamp == other.stamp


def save_change(xsaver, projtype, change):
    """
    Save a change.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param change: Change to save.
    @type  change: L{Change}

    @return: Xml node containing the change, if it was allowed to create.
    @rtype:  L{xml.dom.minidom.Node} or C{None}
    """
    if change.case != "" and not projtype.allow_case:
        return None

    node = xsaver.doc.createElement("change")
    node.setAttribute("strname", change.string_name)
    if change.last_upload:
        node.setAttribute("last_upload", "true")
    if change.case != "":
        node.setAttribute("case", change.case)
    if change.user is not None:
        node.setAttribute("user", change.user)

    if xsaver.share_text:
        node.setAttribute("basetext", make_ref_text(xsaver, change.base_text))
    else:
        node.appendChild(make_text_node(xsaver, change.base_text, "basetext", None)[0])

    if change.new_text is not None:
        if xsaver.share_text:
            node.setAttribute("newtext", make_ref_text(xsaver, change.new_text))
        else:
            node.appendChild(make_text_node(xsaver, change.new_text, "newtext", None)[0])

    snode = save_stamp(xsaver, change.stamp)
    node.appendChild(snode)
    return node


def save_change_json(projtype, change):
    """
    Save a change in Json format.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param change: Change to save.
    @type  change: L{Change}

    @return: Node containing the change, if it was allowed to create.
    @rtype:  C{list} or C{None}
    """
    # Never generate shared strings.
    base_text = make_text_node_json(change.base_text)

    if change.new_text is None:
        new_text = None
    else:
        new_text = make_text_node_json(change.new_text)

    snode = save_stamp_json(change.stamp)
    node = [change.string_name, change.last_upload, change.case, change.user, base_text, new_text, snode]
    return node


def load_change(xloader, node):
    """
    Load a change.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Node containing the change.
    @type  node: L{xml.dom.minidom.Node}

    @return: The loaded change.
    @rtype:  L{Change}
    """
    assert node.tagName == "change"
    strname = node.getAttribute("strname")
    last_upload = loader.get_opt_DOMattr(node, "last_upload", "")
    case = loader.get_opt_DOMattr(node, "case", "")
    user = loader.get_opt_DOMattr(node, "user", None)

    base_text = loader.get_opt_DOMattr(node, "basetext", None)
    if base_text is not None:
        base_text = get_text(xloader, base_text)
    else:
        base_text = get_text_node(xloader, loader.get_single_child_node(node, "basetext"))

    new_text = loader.get_opt_DOMattr(node, "newtext", None)
    if new_text is not None:
        new_text = get_text(xloader, new_text)
    else:
        new_text = loader.get_single_child_node(node, "newtext", True)
        if new_text is not None:
            new_text = get_text_node(xloader, new_text)

    stamp = loader.get_single_child_node(node, "stamp")
    stamp = load_stamp(xloader, stamp)
    return Change(strname, case, base_text, new_text, stamp, user, last_upload == "true")


def load_change_json(node):
    """
    Load a change.

    @param node: Node containing the change.
    @type  node: C{list}

    @return: The loaded change.
    @rtype:  L{Change}
    """
    assert len(node) == 7
    strname = node[0]
    last_upload = node[1]
    case = node[2]
    user = node[3]
    base_text = get_text_node_json(node[4])

    new_text = node[5]
    if new_text is not None:
        new_text = get_text_node_json(new_text)

    stamp = load_stamp_json(node[6])
    return Change(strname, case, base_text, new_text, stamp, user, last_upload)


class Text:
    """
    Text of a string in a language.

    @ivar text: The actual text.
    @type text: C{str}

    @ivar case: Case of this string.
    @type case: C{str}

    @ivar stamp: Time stamp of creation of this text.
    @type stamp: L{Stamp}
    """

    __slots__ = ("text", "case", "stamp")

    def __init__(self, text, case, stamp):
        self.text = sys.intern(text)
        self.case = sys.intern(case)
        self.stamp = stamp

    def __str__(self):
        return "Text(text={!r}, case={!r})".format(self.text, self.case)

    def __eq__(self, other):
        if not isinstance(other, Text):
            return
        return self.text == other.text and self.case == other.case and self.stamp == other.stamp

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.text) + hash(self.case) + hash(self.stamp)


def make_text_node(xmlsaver, text, name, number):
    """
    Construct a node containing the provided text.

    @param xmlsaver: Saver class.
    @type  xmlsaver: L{XmlSaver}

    @param text: Text to save.
    @type  text: L{Text}

    @param name: Name of the node for storing the text.
    @type  name: C{str}

    @param number: Number to refer to the text. Use {@code None} to suppress creating a reference.
    @type  number: C{int} or C{None}

    @return: Node containing the text, and the reference string with the number or C{None}.
    @rtype:  L{xml.dom.minidom.Node}, (C{str} or C{None})
    """
    node = xmlsaver.doc.createElement(name)
    if text.case != "":
        node.setAttribute("case", text.case)

    if number is not None:
        ref = "text_{:04d}".format(number)
        node.setAttribute("ref", ref)
    else:
        ref = None

    stamp = save_stamp(xmlsaver, text.stamp)
    node.appendChild(stamp)
    tnode = xmlsaver.doc.createElement("text")
    node.appendChild(tnode)
    xnode = xmlsaver.doc.createTextNode(text.text)
    tnode.appendChild(xnode)
    return node, ref


def make_text_node_json(text):
    """
    Construct a node containing the provided text.

    @param text: Text to save.
    @type  text: L{Text}

    @return: Node containing the text.
    @rtype:  C{list}
    """
    # Never generate shared text.
    stamp = save_stamp_json(text.stamp)
    node = [text.case, text.text, stamp]
    return node


def make_ref_text(xsaver, text):
    """
    Construct a reference to a text node.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param text: Text node.
    @type  text: L{Text}

    @return: Reference to the actual text.
    @rtype:  C{str}
    """
    return xsaver.get_textref(text)


def get_text_node(xloader, node):
    """
    Load a text node (written by L{make_text_node}).

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Text node to load.
    @type  node: L{xml.dom.minidom.Node}

    @return: Text object.
    @rtype:  L{Text}
    """
    case = loader.get_opt_DOMattr(node, "case", "")
    stamp = load_stamp(xloader, loader.get_single_child_node(node, "stamp"))
    txt = loader.get_single_child_node(node, "text")
    txt = loader.collect_text_DOM(txt)
    txt = language_file.sanitize_text(txt)
    return Text(txt, case, stamp)


def get_text_node_json(node):
    """
    Load text node (written by L{make_text_node_json}).

    @param node: Text node to load.
    @type  node: C{list}

    @return: Text object.
    @rtype:  L{Text}
    """
    assert len(node) == 3
    case = node[0]
    txt = node[1]
    txt = language_file.sanitize_text(txt)
    stamp = load_stamp_json(node[2])
    return Text(txt, case, stamp)


def get_text(xloader, ref):
    """
    Get the text referenced by L{ref}.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param ref: Text of the reference.
    @type  ref: C{str}

    @return: Text object being referenced.
    @rtype:  L{Text}
    """
    return xloader.get_textref(ref)


class Stamp:
    """
    Time stamp.

    @ivar seconds: Time in seconds since epoch.
    @type seconds: C{int}

    @ivar number: Index number, to allow more than one operation in a second.
    @type number: C{int}
    """

    __slots__ = ("seconds", "number")

    def __init__(self, seconds, number):
        self.seconds = seconds
        self.number = number

    def __lt__(self, other):
        if not isinstance(other, Stamp):
            return
        return self.seconds < other.seconds or (self.seconds == other.seconds and self.number < other.number)

    def __eq__(self, other):
        if not isinstance(other, Stamp):
            return
        return self.seconds == other.seconds and self.number == other.number

    def __str__(self):
        return time.asctime(time.gmtime(self.seconds))

    def __hash__(self):
        return (self.seconds << 4) | self.number


last_stamp = 0  # A loooooong time ago.
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


def load_stamp(xloader, node):
    """
    Load a time stamp.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Node containing the time stamp.
    @type  node: L{xml.dom.minidom.Node}

    @return: Loaded time stamp.
    @rtype:  L{Stamp}
    """
    assert node.tagName == "stamp"
    seconds = int(node.getAttribute("second"), 10)
    number = int(loader.get_opt_DOMattr(node, "number", "0"), 10)
    return xloader.get_stamp(seconds, number)


def load_stamp_json(node):
    """
    Convert a time stamp loaded from a Json file into a regular L{Stamp} object.

    @param node: Node containing the time stamp in Json format.
    @type  node: List with two integers (seconds and index).

    @return: The loaded time stamp.
    @rtype:  L{Stamp}
    """
    global last_stamp, last_index

    if last_stamp < node[0]:
        last_stamp = node[0]
        last_index = node[1]
    elif last_stamp == node[0] and last_index < node[1]:
        last_index = node[1]

    return Stamp(node[0], node[1])


def save_stamp(xsaver, stamp):
    """
    Construct an xml representation of the L{stamp} object.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param stamp: Time stamp object to save.
    @type  stamp: L{Stamp}

    @return: The created xml representation.
    @rtype:  L{xml.dom.minidom.Node}
    """
    node = xsaver.doc.createElement("stamp")
    node.setAttribute("second", str(stamp.seconds))
    if stamp.number > 0:
        node.setAttribute("number", str(stamp.number))
    return node


def save_stamp_json(stamp):
    """
    Convert time stamp to Json format.

    @param stamp: Time stamp object to save.
    @type  stamp: L{Stamp}

    @return: The created Json representation.
    @rtype:  list with 2 integers (seconds and index number).
    """
    return [stamp.seconds, stamp.number]


def encode_stamp(stamp):
    """
    Encode a time stamp to the normalized format (RFC 8601).

    @param stamp: Time stamp to convert.
    @type  stamp: L{Stamp}

    @return: Encoded time stamp.
    @rtype:  C{str}
    """
    elems = time.gmtime(stamp.seconds)
    text = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}"
    text = text.format(elems.tm_year, elems.tm_mon, elems.tm_mday, elems.tm_hour, elems.tm_min, elems.tm_sec)
    if stamp.number == 0:
        return text + "Z"
    return text + ".{:d}Z".format(stamp.number)  # No comma, since the text is put into a CSV line.


def decode_stamp(text):
    """
    Decode a text to its time stamp.

    @param text: Text string containing the time stamp.
    @type  text: C{str}

    @return: Decode time stamp, if it could be decoded.
    @rtype:  L{Stamp} or C{None}
    """
    m = re.search("\\.([0-9]+)Z$", text)
    if m:
        val = int(m.group(1), 10)
        text = text[: m.start(0)] + "Z"
    else:
        val = 0

    try:
        elems = time.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None

    secs = calendar.timegm(elems)
    return Stamp(secs, val)
