"""
Project data.
"""
import time, re, calendar
from xml.dom import minidom
from xml.dom.minidom import Node
from webtranslate import loader, project_type
from webtranslate.newgrf import language_file

def load_file(fname):
    """
    Load a project with everything in it.

    @param fname: File to load.
    @type  fname: C{str}

    @return: The loaded project.
    @rtype:  L{Project}
    """
    xloader = XmlLoader()
    return xloader.load_project(fname)

def save_file(proj, fname):
    """
    Save the project to the file.

    @param proj: The project to save.
    @type  proj: L{Project}

    @param fname: Name of the file to write.
    @type  fname: C{str}
    """
    xsaver = XmlSaver()
    doc = xsaver.save_project(proj)

    handle = open(fname, 'w', encoding = "utf-8")
    handle.write(doc.toprettyxml())
    handle.close()

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
    for chg in chgs:
        if chg.case != case: continue
        if best is None or best.stamp < chg.stamp: best = chg

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
            if bchg is not None and chg.base_text != bchg.base_text: continue
            clist = cases.get(chg.case)
            if clist is not None: clist.append(chg)

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
    cases[''] = None

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
    """
    def __init__(self, code, name, description):
        self.code = code
        self.name = name
        self.description = description


MISSING_OK =  0 # String is missing, but that's allowed (non-default case string).
UNKNOWN =     1 # String has unknown state.
UP_TO_DATE =  2 # String is newer than the base string.
OUT_OF_DATE = 3 # String is older than the base string.
INVALID =     4 # String is invalid relative to the base string.
MISSING =     5 # The default case string is missing.

STATUSES = [StatusDefinition(MISSING_OK,  'Omitted',  'The case was not needed in the translation'),
            StatusDefinition(UNKNOWN,     'Unknown',  'The state of the translation was not decidable'),
            StatusDefinition(UP_TO_DATE,  'Correct',  'The string is technically correct and up to date'),
            StatusDefinition(OUT_OF_DATE, 'Outdated', 'A valid translation exists, but it needs review as a newer base language text is available'),
            StatusDefinition(INVALID,     'Invalid',  'A translation exists, but its string parameters do not match with the base language'),
            StatusDefinition(MISSING,     'Missing',  'No translation could be found'),]

STATE_MAP = dict((sd.code, sd) for sd in STATUSES)


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
        results[case] = get_string_status(projtype, chg, case, lng, base_text, binfo)
    return results

def get_string_status(projtype, lchg, case, lng, btext, binfo):
    """
    Get the status of a language string. Also collect its errors.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param lchg: Translation language change to examine.
    @type  lchg: L{Change}

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
    if case == '':
        if lchg is None:
            return MISSING, []
    elif lchg is None or lchg.new_text.text == '':
        return MISSING_OK, []

    if lchg.base_text != btext or lchg.stamp < btext.stamp:
        state = OUT_OF_DATE
    else:
        state = UP_TO_DATE

    linfo = language_file.check_string(projtype, lchg.new_text.text, lchg.case == '', binfo.extra_commands, lng)
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

    @return: The numeric value of the number if it is convertable.
    @rtype:  C{int} or the provided default
    """
    if txt is None: return default
    m = re.match("\\d+$", txt)
    if not m: return default
    return int(txt, 10)

# {{{ class XmlLoader:
class XmlLoader:
    """
    Helper class to load a project from an XML file.

    @ivar stamps: Time stamps loaded so far, mapping of seconds and indices to L{Stamp}.
    @type stamps: C{dict} of (C{int}, C{int}) to L{Stamp}

    @ivar texts: Loaded texts, ordered by their reference.
    @type texts: C{dict} of C{str} to L{Text}
    """
    def __init__(self):
        self.stamps = {}

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

        @return: The loaded project.
        @rtype:  L{Project}
        """
        data = loader.load_dom(fname)
        pnode = loader.get_single_child_node(data, 'project')
        self.stamps = {}

        # Load texts
        self.texts = {}
        texts = loader.get_single_child_node(pnode, 'texts')
        if texts is not None:
            for node in loader.get_child_nodes(texts, 'string'):
                ref = node.getAttribute('ref')
                case = loader.get_opt_DOMattr(node, 'case', '')
                stamp = load_stamp(self, loader.get_single_child_node(node, 'stamp'))
                txt = loader.get_single_child_node(node, 'text')
                txt = loader.collect_text_DOM(txt)
                txt = language_file.sanitize_text(txt)
                self.texts[ref] = Text(txt, case, stamp)

        return load_project(self, pnode)

    def get_textref(self, ref):
        """
        Get the text object associated with the L{ref} string.

        @param ref: Reference name of the text.
        @type  ref: C{str}

        @return: The text object belonging to the reference.
        @rtype:  L{Text}
        """
        return self.texts[ref]
# }}}
# {{{ class XmlSaver:
class XmlSaver:
    """
    Saver helper class, storing the top-level document, and the referenced texts.

    @ivar doc: Xml document node.
    @type doc: L{xml.dom.minidom.Document}

    @ivar texts_node: Node containing the texts.
    @type texts_node: L{xml.dom.minidom.Node}

    @ivar texts: Text references of the project, ordered by text object.
    @type texts: C{dict} of L{Text} to C{str}

    @ivar number: Number for creating unique text references.
    @type number: C{int}
    """
    def __init__(self):
        self.doc = None
        self.texts_node = None
        self.texts = {}
        self.number = 1

    def save_project(self, project):
        """
        Save a project as xml doc document.

        @param project: Project to save.
        @type  project: L{Project}

        @return: Xml document.
        @rtype:  L{xml.dom.minidom.Document}
        """
        self.doc = minidom.Document()
        self.texts_node = self.doc.createElement('texts')
        self.texts = {}
        self.number = 1

        node = save_project(self, project)
        node.appendChild(self.texts_node)
        self.doc.appendChild(node)
        return self.doc

    def get_textref(self, text):
        """
        Construct a node containing the text, and return a reference to it.

        @param text: Text to save.
        @type  text: L{Text}

        @return: Reference to the text node.
        @rtype:  C{str}
        """
        ref = self.texts.get(text)
        if ref is not None: return ref

        node = self.doc.createElement('string')
        if text.case != '': node.setAttribute('case', text.case)

        ref = "text_{:04d}".format(self.number)
        self.number = self.number + 1
        node.setAttribute('ref', ref)

        stamp = save_stamp(self, text.stamp)
        node.appendChild(stamp)
        tnode = self.doc.createElement('text')
        node.appendChild(tnode)
        xnode = self.doc.createTextNode(text.text)
        tnode.appendChild(xnode)

        self.texts_node.appendChild(node)
        self.texts[text] = ref
        return ref
# }}}

# {{{ Project
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
    """
    def __init__(self, human_name, projtype, url=''):
        self.human_name = human_name
        self.projtype = projtype
        self.url = url
        self.statistics = {}
        self.languages = {}
        self.base_language = None
        self.normalized = None # Created while creating 'word_scores'
        self.word_scores = None

        self.skeleton = []

    def get_base_language(self):
        """
        Get the base language of the project.

        @return: The base language of the project, if it exists.
        @rtype:  L{Language} or C{None}
        """
        if self.base_language is None: return None
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
        if self.word_scores is not None: return
        blng = self.get_base_language()
        if blng is None: return

        self.normalized = {} # Mapping of string name to its words.
        for sname, chgs in blng.changes.items():
            chg = get_newest_change(chgs, '')
            assert chg is not None
            line = re.sub('{([^}]*)}', " ", chg.base_text.text)
            words = [word.lower() for word in re.split('\\W+', line) if len(word) > 3]
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
                scores[sname] = 1.0 # The string has this word.

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
        if self.word_scores is None: return []

        words = self.normalized.get(sname)
        if words is None: return []

        strings = {} # Mapping of other strings to cumulative score.
        for word in words:
            for sname2, score2 in self.word_scores[word].items():
                if sname != sname2:
                    val = strings.get(sname2, 0.0)
                    strings[sname2] = val + score2
        best = (None, 0.0)
        best = [best, best, best, best, best]
        for sname, score in strings.items():
            i = 5 # Position of the entry is 'i'
            while i > 0 and score > best[i - 1][1]:
                i = i - 1
            if i > 4:
                continue
            elif i == 4:
                best[4] = (sname, score)
            else:
                best = best[:i] + [(sname, score)] + best[i:-1]

        return [b[0] for b in best if b[0] is not None]

def load_project(xloader, node):
    """
    Load a project node from the Xml file.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Node containing the time stamp.
    @type  node: L{xml.dom.minidom.Node}

    @return: Loaded project
    @rtype:  L{Project}
    """
    assert node.tagName == 'project'
    human_name = node.getAttribute('name')
    projtype = project_type.project_types[loader.get_opt_DOMattr(node, 'projtype', 'newgrf')]
    url = node.getAttribute('url')
    project = Project(human_name, projtype, url)

    langnodes = loader.get_child_nodes(node, 'language')
    project.languages = {}
    for lnode in langnodes:
        lng = load_language(xloader, lnode)
        project.languages[lng.name] = lng

    baselang = loader.get_opt_DOMattr(node, 'baselang', None)
    if baselang is None or baselang not in project.languages:
        baselang = None
        if len(project.languages) > 0:
            print("Project \"" + project.human_name + "\" has no base language, dropping all translations")
            project.languages = {}
            return project # Also skip loading the skeleton.
    project.base_language = baselang
    project.flush_related_cache()

    skelnode = loader.get_single_child_node(node, 'skeleton')
    if skelnode is None:
        project.skeleton = []
    else:
        project.skeleton = load_skeleton(xloader, skelnode)
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
    assert node.tagName == 'skeleton'
    skeleton = []
    for lnode in node.childNodes:
        if lnode.nodeType != Node.ELEMENT_NODE: continue
        if lnode.tagName == 'literal':
            text = loader.collect_text_DOM(lnode)
            skeleton.append(('literal', text))
        elif lnode.tagName == 'string':
            column = convert_num(loader.get_opt_DOMattr(lnode, 'column', '40'), 40)
            name = lnode.getAttribute('name')
            if name is not None: skeleton.append(('string', (column, name)))
        elif lnode.tagName in ('grflangid', 'plural', 'case', 'gender'):
            skeleton.append((lnode.tagName, ''))
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
    node = xsaver.doc.createElement('project')
    node.setAttribute('name', proj.human_name)
    node.setAttribute('projtype', proj.projtype.name)
    node.setAttribute('url', proj.url)
    blng = proj.get_base_language()
    if blng is not None:
        node.setAttribute('baselang', blng.name)

    # Save languages in alphabetical order
    langs = list(proj.languages.items())
    langs.sort()
    for lang in langs:
        lnode = save_language(xsaver, lang[1])
        node.appendChild(lnode)

    skelnode = save_skeleton(xsaver, proj.skeleton)
    node.appendChild(skelnode)
    return node

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
    root = xsaver.doc.createElement('skeleton')
    for stp, sparm in skel:
        node = xsaver.doc.createElement(stp)
        if stp == 'literal' and len(sparm) > 0:
            txt = xsaver.doc.createTextNode(sparm)
            node.appendChild(txt)
        elif stp == 'string':
            column, sname = sparm
            node.setAttribute('name', sname)
            node.setAttribute('column', str(column))

        root.appendChild(node)
    return root

# }}}
# {{{ Language
class Language:
    """
    A language in a project.

    @ivar name: Name of the language (isocode).
    @type name: C{str}

    @ivar grflangid: Language id.
    @type grflangid: C{int}

    @ivar plural: Plural number of the language, if specified.
    @type plural: C{int} or C{None}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language (sorted).
    @type case: C{list} of C{str}

    @ivar changes: Changes to this language ordered by string name, for strings
                   that exist in the language.
    @type changes: C{map} of C{str} to (C{list} of L{Change} or C{None})

    @note: L{case} is sorted to make 'download language' output the default case first,
           which NML more happy.
    """
    def __init__(self, name):
        self.name = name
        self.grflangid = 0x7F
        self.plural = None
        self.gender = []
        self.case  = ['']
        self.changes = {}

def save_language(xsaver, lang):
    """
    Save the language to Xml.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

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

    node = xsaver.doc.createElement('language')
    node.setAttribute('name', lang.name)
    node.setAttribute('langid', str(lang.grflangid))
    if lang.plural is not None:
        node.setAttribute('plural', str(lang.plural))
    if len(lang.gender) > 0:
        node.setAttribute('gender', " ".join(lang.gender))
    cases = [c for c in lang.case if c != '']
    if len(cases) > 0:
        node.setAttribute('cases', " ".join(cases))
    # Sort the strings of the language.
    changes = list(lang.changes.items())
    changes.sort()
    for chgs in changes:
        chgs[1].sort() # Sort changes
        for chg in chgs[1]:
            cnode = save_change(xsaver, chg)
            node.appendChild(cnode)
    return node

def load_language(xloader, node):
    """
    Load a language from the given xml node.

    @param xloader: Loader helper.
    @type  xloader: L{XmlLoader}

    @param node: Node containing the language.
    @type  node: L{xml.dom.minidom.Node}

    @return: The loaded language.
    @rtype:  L{Language}
    """
    assert node.tagName == 'language'
    name = node.getAttribute('name')

    lng = Language(name)
    lng.grflangid = int(node.getAttribute('langid'), 10)
    plural = loader.get_opt_DOMattr(node, 'plural', None)
    if plural is not None:
        plural = int(plural, 10)
    lng.plural = plural

    gender = loader.get_opt_DOMattr(node, 'gender', None)
    if gender is None:
        lng.gender = []
    else:
        lng.gender = gender.split(' ')

    case = loader.get_opt_DOMattr(node, 'cases', None)
    if case is None or case == '':
        lng.case = ['']
    else:
        lng.case = case.split(' ') + ['']
        lng.case.sort()

    lng.changes = {}
    for ch_node in loader.get_child_nodes(node, 'change'):
        change = load_change(xloader, ch_node)
        chgs = lng.changes.get(change.string_name)
        if chgs is None:
            lng.changes[change.string_name] = [change]
        else:
            chgs.append(change)

    return lng
# }}}
# {{{ Change
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
    def __init__(self, string_name, case, base_text, new_text, stamp, user, last_upload = False):
        assert string_name is not None
        self.string_name = string_name
        self.case = case
        self.base_text = base_text
        self.new_text = new_text
        self.stamp = stamp
        self.user = user
        self.last_upload = last_upload

    def __str__(self):
        return "Change('{}', base={}, new={})".format(self.string_name, str(self.base_text), str(self.new_text))

    def __lt__(self, other):
        if not isinstance(other, Change): return False
        return self.stamp < other.stamp

    def __eq__(self, other):
        if not isinstance(other, Change): return False
        return self.stamp == other.stamp


def save_change(xsaver, change):
    """
    Save a change.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param change: Change to save.
    @type  change: L{Change}

    @return: Xml node containing the change.
    @rtype:  L{xml.dom.minidom.Node}
    """
    node = xsaver.doc.createElement('change')
    node.setAttribute('strname', change.string_name)
    if change.last_upload: node.setAttribute('last_upload', 'true')
    if change.case != '': node.setAttribute('case', change.case)
    if change.user is not None: node.setAttribute('user', change.user)

    node.setAttribute('basetext', make_ref_text(xsaver, change.base_text))
    if change.new_text is not None:
        node.setAttribute('newtext', make_ref_text(xsaver, change.new_text))

    snode = save_stamp(xsaver, change.stamp)
    node.appendChild(snode)
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
    assert node.tagName == 'change'
    strname = node.getAttribute('strname')
    last_upload = loader.get_opt_DOMattr(node, 'last_upload', '')
    case = loader.get_opt_DOMattr(node, 'case', '')
    user = loader.get_opt_DOMattr(node, 'user', None)
    base_text = get_text(xloader, node.getAttribute('basetext'))
    new_text = loader.get_opt_DOMattr(node, 'newtext', None)
    if new_text is not None:
        new_text = get_text(xloader, new_text)
    stamp = loader.get_single_child_node(node, 'stamp')
    stamp = load_stamp(xloader, stamp)
    return Change(strname, case, base_text, new_text, stamp, user, last_upload == 'true')

# }}}
# {{{ Text (references)
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
    def __init__(self, text, case, stamp):
        self.text = text
        self.case = case
        self.stamp = stamp

    def __str__(self):
        return "Text(text={!r}, case={!r})".format(self.text, self.case)

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

# }}}
# {{{ Time stamps
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

    def __lt__(self, other):
        if not isinstance(other, Stamp): return False
        return self.seconds < other.seconds or \
               (self.seconds == other.seconds and self.number < other.number)

    def __eq__(self, other):
        if not isinstance(other, Stamp): return False
        return self.seconds == other.seconds and self.number == other.number

    def __str__(self):
        return time.asctime(time.gmtime(self.seconds))

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
    assert node.tagName == 'stamp'
    seconds = int(node.getAttribute('second'), 10)
    number = int(loader.get_opt_DOMattr(node, 'number', '0'), 10)
    return xloader.get_stamp(seconds, number)

def save_stamp(xsaver, stamp):
    """
    Construct an xml representation of the L{stamp} object.

    @param xsaver: Saver class.
    @type  xsaver: L{XmlSaver}

    @param stamp: Text object to save.
    @type  stamp: L{Stamp}

    @return: The created xml representation.
    @rtype:  L{xml.dom.minidom.Node}
    """
    node = xsaver.doc.createElement('stamp')
    node.setAttribute('second', str(stamp.seconds))
    if stamp.number > 0:
        node.setAttribute('number', str(stamp.number))
    return node

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
    return text + ".{:d}Z".format(stamp.number) # No comma, since the text is put into a CSV line.

def decode_stamp(text):
    """
    Decode a text to its time stamp.

    @param text: Text string containing the time stamp.
    @type  text: C{str}

    @return: Decode time stamp, if it could be decoded.
    @rtype:  L{Stamp} or C{None}
    """
    m = re.search('\\.([0-9]+)Z$', text)
    if m:
        val =  int(m.group(1), 10)
        text = text[:m.start(0)] + 'Z'
    else:
        val = 0

    try:
        elems = time.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None

    secs = calendar.timegm(elems)
    return Stamp(secs, val)

# }}}

