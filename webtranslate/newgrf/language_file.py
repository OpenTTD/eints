"""
Language file processing.
"""
import re, codecs
from webtranslate import project_type
from webtranslate.newgrf import language_info

ERROR = 'Error'
WARNING = 'Warning'

class ErrorMessage:
    """
    Error or warning Message.

    @ivar type: Type of message (L{ERROR} or L{WARNING}).
    @type type: C{str}

    @ivar line: Line number of the message, if available.
    @type line: C{int} or C{None}

    @ivar msg: Human readable error/warning message.
    @type msg: C{str}
    """
    def __init__(self, type, line, msg):
        self.type = type
        self.line = line
        self.msg = msg

# {{{ def check_string(text, default_case, extra_commands, lng):
# Number of plural forms for each plural type (C{None} means no plural forms allowed).
plural_count_map = {None: 0, 0: 2, 1: 1, 2: 2, 3: 3, 4: 5, 5: 3, 6: 3, 7: 3, 8: 4, 9: 2, 10: 3, 11: 2, 12: 4, 13: 4}

param_pat = re.compile('{([0-9]+:)?([A-Z_0-9]+)(\\.[A-Za-z0-9]+)?}')
gender_assign_pat = re.compile('{G *= *([^ }]+) *}')
argument_pat = re.compile('[ \\t]+([^"][^ \\t}]*|"[^"}]*")')
end_argument_pat = re.compile('[ \\t]*}')
number_pat = re.compile('[0-9]+$')

def check_string(projtype, text, default_case, extra_commands, lng):
    """
    Check the contents of a single string.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param text: String text.
    @type  text: C{str}

    @param default_case: This string is the default case.
    @type  default_case: C{bool}

    @param extra_commands: Extra commands that are allowed, if supplied.
    @type  extra_commands: C{None} if any extra commands are allowed,
                           C{set} of C{str} if a specific set of extra commands is allowed.

    @param lng: Language containing the string.
    @type  lng: L{Language}

    @return: String parameter information.
    @rtype:  C{NewGrfStringInfo}
    """
    string_info = NewGrfStringInfo(extra_commands)
    plural_count = plural_count_map[lng.plural]
    pos = 0 # String parameter number.
    idx = 0 # Text string index.
    while idx < len(text):
        i = text.find('{', idx)
        if i == -1: break
        if i > 0: idx = i

        # text[idx] == '{', now find matching '}'
        if text.startswith('{}', idx):
            string_info.add_nonpositional(project_type.NL_PARAMETER)
            idx = idx + 2
            continue

        if text.startswith('{{}', idx):
            string_info.add_nonpositional(project_type.CURLY_PARAMETER)
            idx = idx + 3
            continue

        m = param_pat.match(text, idx)
        if m:
            if m.group(1) is None:
                argnum = None
            else:
                argnum = int(m.group(1)[:-1], 10)

            if m.group(3) is None:
                case = None
            else:
                case = m.group(3)[1:]

            entry = projtype.text_commands.get(m.group(2))
            if entry is None:
                if argnum is not None:
                    string_info.add_error(ErrorMessage(ERROR, None, "String command {} does not take an argument count".format(m.group(2))))
                    return string_info
                if case is not None:
                    string_info.add_error(ErrorMessage(ERROR, None, "String command {} does not take a case".format(m.group(2))))
                    return string_info

                if not string_info.add_extra_command(m.group(2)):
                    return string_info
                idx = m.end()
                continue

            if case is not None:
                if not entry.allow_case:
                    string_info.add_error(ErrorMessage(ERROR, None, "String command {} does not take a case".format(m.group(2))))
                    return string_info
                if case not in lng.case:
                    string_info.add_error(ErrorMessage(ERROR, None, "Case {} of string command {} does not exist in the language".format(case, m.group(2))))
                    return string_info

            if not entry.takes_param:
                if argnum is not None:
                    string_info.add_error(ErrorMessage(ERROR, None, "String command {} does not take an argument count".format(m.group(2))))
                    return string_info

                string_info.add_nonpositional(entry)
            else:
                if argnum is not None: pos = argnum
                string_info.add_positional(pos, entry)
                pos = pos + 1

            idx = m.end()
            continue

        if text.startswith('{P ', idx):
            args = get_arguments(text, 'P', idx + 2, string_info)
            if args is None: return string_info

            args, idx = args
            if plural_count == 0:
                string_info.add_error(ErrorMessage(ERROR, None, "{P ..} cannot be used without defining the plural type with ##plural"))
                return string_info
            elif len(args) > 0:
                # If the first argument is a number, it cannot be a value for the plural command.
                m = number_pat.match(args[0])
                if m:
                    num = int(args[0], 10)
                    args = args[1:]
                else:
                    num = pos - 1

                if len(args) == plural_count:
                    string_info.add_plural(num)
                    continue

            string_info.add_error(ErrorMessage(ERROR, None, "Expected {} string arguments for {{P ..}}, found {} arguments".format(plural_count, len(args))))
            return string_info

        # {G=...}
        m = gender_assign_pat.match(text, idx)
        if m:
            if idx != 0:
                string_info.add_error(ErrorMessage(ERROR, None, "{} may only be used at the start of a string".format(m.group(0))))
                return string_info
            if not default_case:
                string_info.add_error(ErrorMessage(ERROR, None, '{G=..} may only be used for the default string (that is, without case extension)'))
                return string_info
            if m.group(1) not in lng.gender:
                string_info.add_error(ErrorMessage(ERROR, None, "Gender {} is not listed in ##gender".format(m.group(1))))
                return string_info

            idx = m.end()
            continue

        if text.startswith('{G ', idx):
            assert text[idx:idx+2] != '{G='
            args = get_arguments(text, 'G', idx + 2, string_info)
            if args is None: return string_info

            args, idx = args
            expected = len(lng.gender)
            if expected == 0:
                string_info.add_error(ErrorMessage(ERROR, None, "{G ..} cannot be used without defining the genders with ##gender"))
                return string_info
            elif len(args) > 0:
                # If the first argument is a number, it cannot be a value for the plural command.
                m = number_pat.match(args[0])
                if m:
                    num = int(args[0], 10)
                    args = args[1:]
                else:
                    num = pos

                if len(args) == expected:
                    string_info.add_gender(num)
                    continue

            string_info.add_error(ErrorMessage(ERROR, None, "Expected {} string arguments for {{G ..}}, found {} arguments".format(expected, len(args))))
            return string_info


        string_info.add_error(ErrorMessage(ERROR, None, "Unknown {...} command found in the string"))
        return string_info

    string_info.check_sanity(projtype)
    return string_info

# {{{ def get_arguments(text, cmd, idx, string_info):
def get_arguments(text, cmd, idx, string_info):
    """
    Get arguments of a C{"{P"} or C{"{G"}.

    @param text: String text.
    @type  text: C{str}

    @param cmd: Command being parsed ('P' or 'G').
    @type  cmd: C{str}

    @param idx: Index in the text to start searching.
    @type  idx: C{int}

    @param string_info: Class collecting the string information.
    @type  string_info: L{NewGrfStringInfo}

    @return: Found arguments and new index, or C{None} if an error was found.
    @rtype:  (C{list} of C{str}, C{int}) or C{None}
    """
    args = []
    while idx < len(text):
        m = end_argument_pat.match(text, idx)
        if m:
            return args, m.end()
        m = argument_pat.match(text, idx)
        if m:
            args.append(m.group(1)) # Do not strip quotes to keep the difference between {P 0 ..} and {P "0" ..}.
            idx = m.end()
            continue

        string_info.add_error(ErrorMessage(ERROR, None, "Error while parsing arguments of a '{}' command".format('{' + cmd + '..}')))
        return None

    string_info.add_error(ErrorMessage(ERROR, None, "Missing the terminating '}}' while parsing arguments of a '{}' command".format('{' + cmd + '..}')))
    return None

# }}}
# {{{ class NewGrfStringInfo:
class NewGrfStringInfo:
    """
    @ivar allowed_extra: Extra commands that are allowed, if supplied.
    @type allowed_extra: C{None} if any extra commands are allowed,
                         C{set} of C{str} if a specific set of extra commands is allowed.

    @ivar genders: String parameters used for gender queries.
    @type genders: C{list} of C{bool}

    @ivar plurals: String parameters used for plural queries.
    @type plurals: C{list} of C{bool}

    @ivar commands: String commands at each position.
    @type commands: C{list} of C{str}

    @ivar non_positionals: Mapping of commands without position to their count.
    @type non_positionals: C{dict} of C{str} to C{int}

    @ivar extra_commands: Found extra commands.
    @type extra_commands: C{set} of C{str}

    @ivar errors: Detected errors in the string.
    @type errors: c{list} of L{ErrorMessage}

    @ivar has_error: Whether the L{errors} list has a real error.
    @type has_error: C{bool}
    """
    def __init__(self, allowed_extra):
        self.allowed_extra = allowed_extra
        self.genders  = []
        self.plurals  = []
        self.commands = []
        self.non_positionals = {}
        self.extra_commands = set()
        self.errors = []
        self.has_error = False

    def __str__(self):
        rv = []
        if len(self.genders) > 0: rv.append("gender=" + str(self.genders))
        if len(self.plurals) > 0: rv.append("plural=" + str(self.plurals))
        if len(self.commands) > 0: rv.append("commands=" + str(self.commands))
        if len(self.non_positionals) > 0: rv.append("non-pos=" + str(self.non_positionals))
        if len(self.extra_commands) > 0: rv.append("extra=" + str(self.extra_commands))
        return "**strinfo(" + ", ".join(rv) + ")"

    def add_error(self, errmsg):
        """
        Add an error/warning to the list of detected errors.

        @param errmsg: Error message to add.
        @type  errmsg: L{ErrorMessage}
        """
        if errmsg.type == ERROR:
            self.has_error = True

        self.errors.append(errmsg)

    def add_gender(self, pos):
        """
        Add a gender query for parameter L{pos}.

        @param pos: String parameter number used for gender query.
        @type  pos: C{int}
        """
        if pos not in self.genders:
            self.genders.append(pos)

    def add_plural(self, pos):
        """
        Add a plural query for parameter L{pos}.

        @param pos: String parameter number used for plural query.
        @type  pos: C{int}
        """
        if pos not in self.plurals:
            self.plurals.append(pos)

    def add_nonpositional(self, cmd):
        """
        Add a non-positional string command.

        @param cmd: Command to add.
        @type  cmd: L{ParameterInfo}
        """
        cnt = self.non_positionals.get(cmd.literal, 0)
        self.non_positionals[cmd.literal] = cnt + 1

    def add_extra_command(self, cmdname):
        """
        Add an extra command (a custom tag). The command is always non-positional.

        @param cmdname: Name of the command.
        @type  cmdname: C{str}

        @return: Whether the command was correct.
        @rtype:  C{bool}
        """
        if self.allowed_extra is None: # Allow any additional command.
            self.extra_commands.add(cmdname)
        elif cmdname not in self.allowed_extra:
            self.add_error(ErrorMessage(ERROR, None, "Unknown string command {} found".format("{" + cmdname + "}")))
            return False

        cnt = self.non_positionals.get(cmdname, 0)
        self.non_positionals[cmdname] = cnt + 1
        return True

    def add_positional(self, pos, cmd):
        """
        Add a string command at the stated position.

        @param pos: String parameter number.
        @type  pos: C{int}

        @param cmd: String command used at the stated position.
        @type  cmd: C{ParameterInfo}

        @return: Whether the command was correct.
        @rtype:  C{bool}
        """
        if pos < len(self.commands):
            if self.commands[pos] is None:
                self.commands[pos] = cmd.literal
                return True
            if self.commands[pos] != cmd.literal:
                self.add_error(ErrorMessage(ERROR, None, "String parameter {} has more than one string command".format(pos)))
                return False
            return True
        while pos > len(self.commands): self.commands.append(None)
        self.commands.append(cmd.literal)
        return True

    def check_sanity(self, projtype):
        """
        Check sanity of the string commands and parameters.

        @param projtype: Project type.
        @type  projtype: L{ProjectType}
        """
        ok = True
        for pos, cmd in enumerate(self.commands):
            if cmd is None:
                self.add_error(ErrorMessage(ERROR, None, "String parameter {} has no string command".format(pos)))
                ok = False
        if ok:
            for pos in self.plurals:
                if pos < 0 or pos >= len(self.commands):
                    self.add_error(ErrorMessage(ERROR, None, "String parameter {} is out of bounds for plural queries {{P ..}}".format(pos)))
                    ok = False
                    continue

                parm = projtype.text_commands[self.commands[pos]]
                if not parm.use_plural:
                    self.add_error(ErrorMessage(ERROR, None, "String parameter {} may not be used for plural queries {{P ..}}".format(pos)))
                    ok = False

        if ok:
            for pos in self.genders:
                if pos < 0 or pos >= len(self.commands):
                    self.add_error(ErrorMessage(ERROR, None, "String parameter {} is out of bounds for gender queries {{G ..}}".format(pos)))
                    continue

                parm = projtype.text_commands[self.commands[pos]]
                if not parm.use_gender:
                    self.add_error(ErrorMessage(ERROR, None, "String parameter {} may not be used for gender queries {{G ..}}".format(pos)))
# }}}
# }}}

# {{{ class StringValue:
class StringValue:
    """
    Value of a string.

    @ivar lnum: Line number (0-based).
    @type lnum: C{int}

    @ivar name: Name of the string.
    @type name: C{str}

    @ivar case: Case of the string, if any.
    @type case: C{str}

    @ivar text: Actual text of the string.
    @type text: C{str}
    """
    def __init__(self, lnum, name, case, text):
        self.lnum = lnum
        self.name = name
        self.case = case
        self.text = text

# }}}
# {{{ class NewGrfData:
class NewGrfData:
    """
    Data of a NewGRF language.

    @ivar grflangid: Language number.
    @type grflangid: C{int}

    @ivar language_data: Technical information about the language definition.
    @type language_data: L{LanguageData} or C{None}

    @ivar plural: Plural type, if specified.
    @type plural: C{int} (0..12 inclusive) or C{None}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language.
    @type case: C{list} of C{str}

    @ivar skeleton: Skeleton file.
    @type skeleton: @type skeleton: C{list} of (C{str}, C{str}), where the first string is a
                    type:
                     - 'literal':   Line literally copied
                     - 'string':    Column with ':', and line with a text string (possibly many when there are cases)
                     - 'grflangid': Line with the language id
                     - 'plural':    Plural number
                     - 'case':      Cases line
                     - 'gender':    Gender line

    @ivar strings: Strings with their line number, name and text.
    @type strings: C{list} of L{StringValue}

    @ivar errors: Errors detected during loading of the file.
    @type errors: C{list} of L{ErrorMessage}
    """
    def __init__(self):
        self.grflangid = None
        self.language_data = None
        self.plural = None
        self.gender = []
        self.case = ['']
        self.skeleton = []
        self.strings = []
        self.errors = []

    def add_error(self, errmsg):
        """
        Add an error/warning to the list of detected errors.

        @param errmsg: Error message to add.
        @type  errmsg: L{ErrorMessage}
        """
        self.errors.append(errmsg)

    def cleanup_skeleton(self):
        """
        Clean up the skeleton file.
        """
        while len(self.skeleton) > 0 and self.skeleton[0][0] == 'literal' and self.skeleton[0][1] == '': del self.skeleton[0]
        while len(self.skeleton) > 0 and self.skeleton[-1][0] == 'literal' and self.skeleton[-1][1] == '': del self.skeleton[-1]

# }}}

# {{{ def load_language_file(handle, max_size):
# {{{ def handle_pragma(lnum, line, data):
def handle_pragma(lnum, line, data):
    """
    Handle a pragma line.

    @param lnum: Line number (0-based).
    @type  lnum: C{int}

    @param line: Text of the line.
    @type  line: C{str}

    @param data: Data store of the properties.
    @type  data: L{NewGrfData}
    """
    line = line.split()
    if line[0] == '##grflangid':
        if len(line) != 2:
            data.add_error(ErrorMessage(ERROR, lnum, "##grflangid takes exactly one argument"))
            return

        # Is the argument a known text-name?
        for entry in language_info.all_languages:
            if entry.isocode == line[1]:
                data.grflangid = entry.grflangid
                data.language_data = entry
                return

        # Is it a number?
        try:
            val = int(line[1], 16)
        except ValueError:
            data.add_error(ErrorMessage(ERROR, lnum, "##grflangid is neither a valid language name nor a language code"))
            return
        for entry in language_info.all_languages:
            if entry.grflangid == val:
                data.grflangid = val
                data.language_data = entry
                return
        # Don't know what it is.
        data.add_error(ErrorMessage(ERROR, lnum, "##grflangid is neither a valid language name nor a language code"))
        return

    if line[0] == '##plural':
        if len(line) != 2:
            data.add_error(ErrorMessage(ERROR, lnum, "##plural takes exactly one numeric argument in the range 0..12"))
            return
        try:
            val = int(line[1], 10)
        except ValueError:
            val = -1
        if val < 0 or val > 12:
            data.add_error(ErrorMessage(ERROR, lnum, "##plural takes exactly one numeric argument in the range 0..12"))
            return
        data.plural = val
        return

    if line[0] == '##gender':
        if len(line) == 1:
            data.add_error(ErrorMessage(ERROR, lnum, "##gender takes a non-empty list of gender names"))
            return
        data.gender = line[1:]
        return

    if line[0] == '##case':
        if len(line) == 1:
            data.add_error(ErrorMessage(ERROR, lnum, "##case takes a non-empty list of case names"))
            return
        data.case = [''] + line[1:]
        return

    data.add_error(ErrorMessage(ERROR, lnum, "Unknown pragma '{}'".format(line[0])))
    return
# }}}

string_pat = re.compile('^([A-Za-z_0-9]+)(\\.[A-Za-z0-9]+)?[ \\t]*:(.*)$')
bom = codecs.BOM_UTF8.decode('utf-8')

def load_language_file(handle, max_size):
    """
    Load a language file.

    @param handle: File handle.
    @type  handle: L{io.BufferedReader}

    @param max_size: Maimum allowed size to read from the handle.
    @type  max_size: C{int}

    @return: Loaded language data.
    @rtype:  L{NewGrfData}
    """
    data = NewGrfData()
    seen_strings = False
    skeleton_strings = set()

    # Ensure the skeleton has all language properties.
    data.skeleton.append(('grflangid', ''))
    data.skeleton.append(('plural', ''))
    data.skeleton.append(('gender', ''))
    data.skeleton.append(('case', ''))

    # Read file, and process the lines.
    text = handle.read(max_size)
    if len(text) == max_size:
        data.add_error(ErrorMessage(ERROR, None, 'File not completely read'))
    text = str(text, encoding = "utf-8")
    for lnum, line in enumerate(text.split('\n')):
        line = line.rstrip()
        if line.startswith(bom):
            line = line[len(bom):]

        if line.startswith('##'):
            if seen_strings:
                data.add_error(ErrorMessage(ERROR, lnum, "Cannot change language properties after processing strings"))
                continue
            handle_pragma(lnum, line, data)
            continue

        if line == "" or line.startswith(';') or line.startswith('#'):
            data.skeleton.append(('literal', line))
            continue

        m = string_pat.match(line) # Regular string line?
        if m:
            seen_strings = True # Disable processing of ## pragma lines
            if m.group(2) is None:
                m2 = ''
            else:
                m2 = m.group(2)[1:]
            sv = StringValue(lnum, m.group(1), m2, m.group(3))
            data.strings.append(sv)
            if m2 is '':
                if m.group(1) in skeleton_strings:
                    data.add_error(ErrorMessage(ERROR, lnum, 'String name {} is already used.'.format(m.group(1))))
                    continue
                skeleton_strings.add(m.group(1))
                if '\t' in line:
                    normalized_line = line.expandtabs()
                else:
                    normalized_line = line
                data.skeleton.append(('string', (normalized_line.find(':'), m.group(1))))
            continue

        data.add_error(ErrorMessage(ERROR, lnum, "Line not recognized"))

    for sv in data.strings:
        if sv.name not in skeleton_strings:
            data.add_error(ErrorMessage(ERROR, None, 'String name \"{}\" has no default definition (that is, without case).'.format(sv.name)))

    if data.language_data is None:
        data.add_error(ErrorMessage(ERROR, None, 'Language file has no ##grflangid'))

    data.cleanup_skeleton()
    return data

# }}}

def sanitize_text(txt):
    """
    Perform some small safe normalizations on the text of a string.

    @param txt: Text to sanitize.
    @type  txt: C{str}

    @return: The sanitized text.
    @rtype:  C{str}
    """
    # Strip trailing white space.
    txt = txt.rstrip()

    # Strip \n and \r from the string.
    txt = txt.replace('\n', '')
    txt = txt.replace('\r', '')

    # Strip white space in front of {}
    txt = re.sub(' +{}', '{}', txt)
    return txt

# Get string information
# {{{ def compare_info(base_info, lng_info):
def compare_info(projtype, base_info, lng_info):
    """
    Compare both string uses with each other. Errors found during the comparison are added to the translation L{lng_info}.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param base_info: Information about string parameters from the base language.
    @type  base_info: L{NewGrfStringInfo}

    @param lng_info: Information about string parameters from the translation.
    @type  lng_info: L{NewGrfStringInfo}

    @return: Whether both parameter uses are compatible.
    @rtype:  C{bool}
    """
    if base_info.has_error: return True # Cannot blame the translation when the base language is broken.
    if lng_info.has_error: return False # Translation has more serious problems.

    if base_info.commands != lng_info.commands:
        if len(base_info.commands) > len(lng_info.commands):
            msg = 'String command for position {} (and further) is missing in the translation'
            msg = msg.format(len(lng_info.commands))
            lng_info.add_error(ErrorMessage(ERROR, None, msg))
            return False
        if len(base_info.commands) < len(lng_info.commands):
            msg = 'String command for position {} (and further) is not used in the base language'
            msg = msg.format(len(base_info.commands))
            lng_info.add_error(ErrorMessage(ERROR, None, msg))
            return False

        for i in range(len(base_info.commands)):
            if base_info.commands[i] != lng_info.commands[i]:
                msg = 'String command for position {} is wrong, base language uses {}, the translation uses {}'
                msg = msg.format(i, '{' + base_info.commands[i] + '}', '{' + lng_info.commands[i] + '}')
                lng_info.add_error(ErrorMessage(ERROR, None, msg))
                return False

        assert False # Never reached

    # Non-positional commands must match in count.
    if base_info.non_positionals != lng_info.non_positionals:
        for bname, bcnt in base_info.non_positionals.items():
            if bname not in lng_info.non_positionals:
                msg = 'String command {} is missing in the translation'.format('{' + bname + '}')
                if is_critical_non_positional(projtype, bname):
                    lng_info.add_error(ErrorMessage(ERROR, None, msg))
                    return False
                else:
                    lng_info.add_error(ErrorMessage(WARNING, None, msg))
            elif lng_info.non_positionals[bname] != bcnt:
                # Non-positional is used both in base language and in translation, but a different number of times.
                # Requiring an exact match would give too much trouble, especially with ltr <-> rtl translations.
                msg = 'String command {} is used {} times in the base language, and {} times in the translation'
                msg = msg.format('{' + bname + '}', bcnt, lng_info.non_positionals[bname])
                lng_info.add_error(ErrorMessage(WARNING, None, msg))

        for np in lng_info.non_positionals:
            if np not in base_info.non_positionals:
                msg = 'String command {} is not used in the base language'.format('{' + np + '}')
                if is_critical_non_positional(projtype, np):
                    lng_info.add_error(ErrorMessage(ERROR, None, msg))
                    return False
                else:
                    lng_info.add_error(ErrorMessage(WARNING, None, msg))

    return True

def is_critical_non_positional(projtype, name):
    """
    Return whether the given non-position string command should match exactly
    in count between the base language and the translation.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param name: String command.
    @type  name: C{str}

    @return: Whether the command should match in count exactly.
    @rtype:  C{bool}
    """
    if name == '':
        sc = project_type.NL_PARAMETER
    elif name == '{':
        sc = project_type.CURLY_PARAMETER
    else:
        sc = projtype.text_commands.get(name)
        if sc is None: return True

    return sc.critical
# }}}
