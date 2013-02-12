"""
Project data.
"""
import time
from xml.dom import minidom
from xml.dom.minidom import Node
from webtranslate import loader
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

    handle = open(fname, 'w')
    handle.write(doc.toprettyxml())
    handle.close()

def get_newest_change(chgs, case):
    """
    Get the newest change matching the case.

    @param chgs: Changes to select from.
    @type  chgs: C{list} of L{Change}

    @param case: Case to match.
    @type  case: C{str} or C{None}

    @return: The newest change, if available.
    @rtype:  C{Change} or C{None}
    """
    best = None
    for chg in chgs:
        if chg.case != case: continue
        if best is None or best.stamp < chg.stamp: best = chg

    return best


def get_all_newest_changes(chgs, cases):
    """
    Get the newest changes for all cases.

    @param chgs: Changes to select from.
    @type  chgs: C{list} of L{Change}

    @param cases: Available cases.
    @type  cases: C{list} of C{str}

    @return: Newest change for each case (for as far as it exists in the given L{chgs}).
    @rtype:  C{dict} of C{str} to (L{Change} or C{None}
    """
    cases = dict((c, None) for c in cases)
    cases[''] = None

    for chg in chgs:
        if chg.case is None:
            cc = ''
        else:
            cc = chg.case

        if cc in cases:
            if cases[cc] is None or cases[cc].stamp < chg.stamp:
                cases[cc] = chg
    return cases

MISSING_OK =  0 # String is missing, but that's allowed (non-default case string).
UP_TO_DATE =  1 # String is newer than the base string.
OUT_OF_DATE = 2 # String is older than the base string.
INVALID =     3 # String is invalid relative to the base string.
MISSING =     4 # The default case string is missing.

def get_base_string_info(text):
    """
    Get the newgrf string information about the given text.
    Assume the string is from the base language.

    @param text: String to examine.
    @type  text: C{str}

    @return: String information.
    @rtype:  L{NewGrfStringInfo}
    """
    return language_file.get_base_string_info(text)


def decide_all_string_status(base_chg, lng_chgs, lng, base_string_info = None):
    """
    Decide the state of all the cases of the string based on the information of L{base_chg} and
    the L{lng_chgs}.

    @param base_chg: Newest version of the string in the base language.
    @type  base_chg: L{Change}

    @param lng_chgs: Newest version of the string in the translation, for all cases.
    @type  lng_chgs: C{dict} of C{str} to (L{Change} or C{None}

    @param lng: Language.
    @type  lng: L{Language}

    @param base_string_info: Optional string information of the base language.
                             Use L{get_base_string_info} to get the information.
    @type  base_string_info: C{None} or L{NewGrfStringInfo}

    @return: Info about each case.
    @rtype:  C{dict} of C{str} to C{int})
    """
    base_text = base_chg.base_text

    results = {}
    for case, chg in lng_chgs.items():
        if chg is None:
            results[case] = MISSING if case == '' else MISSING_OK
            continue

        if chg.new_text != base_text and chg.stamp < base_text.stamp:
            state = OUT_OF_DATE
        else:
            state = UP_TO_DATE

        if base_string_info is None:
            base_string_info = get_base_string_info(base_text.text)
        lng_string_info = language_file.get_translation_string_info(chg.new_text.text, lng)
        if not language_file.compare_info(base_string_info, lng_string_info):
            state = INVALID

        results[case] = state

    return results


# {{{ class XmlLoader:
class XmlLoader:
    """
    Helper class to load a project from an XML file.

    @ivar stamps: Time stamps loaded so far, mapping of seconds and indices to L{Stamp}.
    @type stamps: C{dict} of (C{int, C{int}) to L{Stamp}

    @ivar: texts: Loaded texts, ordered by their reference.
    @type  texts: C{dict} of C{str} to L{Text}
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
                case = loader.get_opt_DOMattr(node, 'case', None)
                stamp = load_stamp(self, loader.get_single_child_node(node, 'stamp'))
                txt = loader.get_single_child_node(node, 'text')
                txt = loader.collect_text_DOM(txt)
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
    @type doc: L{xml.dom.minidom,Document}

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
        if text.case is not None: node.setAttribute('case', text.case)

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

    @ivar name: Project name.
    @type name: C{str}

    @ivar statistics: Statistics for all strings in all languages. Managed by the project
                      meta-data, not stored in the project.
                      Mapping of language name to string name to list of case and state, where
                      the state is UP_TO_DATE, OUT_OF_DATE, INVALID, MISSING_OK, or MISSING.
    @type statistics: C{dict} of C{str} to C{dict} of C{str} to C{list} of (C{str}, C{int})

    @ivar languages: Languages of the project ordered by name (isocode).
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

    def get_base_language(self):
        """
        Get the base language of the project.

        @return: The base language of the project, if it exists.
        @rtype:  L{Language} or C{None}
        """
        if self.base_language is None: return None
        return self.languages.get(self.base_language)


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
    name = node.getAttribute('name')
    project = Project(name)

    langnodes = loader.get_child_nodes(node, 'language')
    project.languages = {}
    for lnode in langnodes:
        lng = load_language(xloader, lnode)
        project.languages[lng.name] = lng

    baselang = loader.get_opt_DOMattr(node, 'baselang', None)
    if baselang is None or baselang not in project.languages:
        baselang = None
        if len(project.languages) > 0:
            print("Project \"" + project.name + "\" has no base language, dropping all translations")
            project.languages = {}
            return project # Also skip loading the skeleton.
    project.base_language = baselang

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
            name = lnode.getAttribute('name')
            if name is not None: skeleton.append(('string', name))
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
    node.setAttribute('name', proj.name)
    blng = proj.get_base_language()
    if blng is not None:
        node.setAttribute('baselang', blng.name)

    for lang in proj.languages.values():
        lnode = save_language(xsaver, lang)
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
            node.setAttribute('name', sparm)

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
    node.setAttribute('plural', str(lang.plural))
    if len(lang.gender) > 0:
        node.setAttribute('gender', " ".join(lang.gender))
    if len(lang.case) > 0:
        node.setAttribute('cases', " ".join(lang.case))
    for chgs in lang.changes.values():
        for chg in chgs:
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
    lng.plural = int(node.getAttribute('plural'), 10)

    gender = loader.get_opt_DOMattr(node, 'gender', None)
    if gender is None:
        lng.gender = []
    else:
        lng.gender = gender.split(' ')

    case = loader.get_opt_DOMattr(node, 'cases', None)
    if case is None:
        lng.case = []
    else:
        lng.case = case.split(' ')

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
    @type user: C{str}
    """
    def __init__(self, string_name, case, base_text, new_text, stamp, user):
        self.string_name = string_name
        self.case = case
        self.base_text = base_text
        self.new_text = new_text
        self.stamp = stamp
        self.user = user

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
    if change.case is not None: node.setAttribute('case', change.case)
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
    case = loader.get_opt_DOMattr(node, 'case', None)
    user = loader.get_opt_DOMattr(node, 'user', None)
    base_text = get_text(xloader, node.getAttribute('basetext'))
    new_text = loader.get_opt_DOMattr(node, 'newtext', None)
    if new_text is not None:
        new_text = get_text(xloader, new_text)
    stamp = loader.get_single_child_node(node, 'stamp')
    stamp = load_stamp(xloader, stamp)
    return Change(strname, case, base_text, new_text, stamp, user)

# }}}
# {{{ Text (references)
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

# }}}

