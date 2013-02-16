"""
Language file processing.
"""
import re, codecs, collections
from webtranslate.newgrf import language_info

ERROR = 'Error'
WARNING = 'Warning'

num_plurals = {0: 2, 1: 1, 2: 2, 3: 3, 4: 5, 5: 3, 6: 3, 7: 3, 8: 4, 9: 2, 10: 3, 11: 2, 12: 4}

param_pat = re.compile('{([0-9]+:)?([A-Z_0-9]*|{)}')
gender_assign_pat = re.compile('{G *= *([^ }]+) *}')
argument_pat = re.compile('[ \\t]+([^"][^ \\t}]*|"[^"}]*")')
end_argument_pat = re.compile('[ \\t]*}')

# {{{ def check_string(text, lnum , default_case, extra_commands, plural_count, gender, errors):
def check_string(text, lnum, default_case, extra_commands, plural_count, gender, errors):
    """
    Check the contents of a single string.

    @param text: String text.
    @type  text: C{str}

    @param lnum: Line number (0-based)
    @type  lnum: C{int} or C{None}

    @param default_case: This string is the default case.
    @type  default_case: C{bool}

    @param extra_commands: Extra commands that are allowed, if supplied.
    @type  extra_commands: C{None} if any extra commands are allowed,
                           C{set} of C{str} if a specific set of extra commands is allowed.

    @param plural_count: Number of plural forms.
    @type  plural_count: C{int}

    @param gender: Names of the gender forms.
    @type  gender: C{list} of C{str}

    @param errors: Errors found so far, list of line numbers + message.
    @type  errors: C{list} of ((C{ERROR} or C{WARNING}, C{int} or C{None}), C{str})

    @return: String parameter information if the string was correct, else C{None}
    @rtype:  C{NewGrfStringInfo} or C{None}
    """
    string_info = NewGrfStringInfo()
    pos = 0 # String parameter number.
    idx = 0 # Text string index.
    while idx < len(text):
        i = text.find('{', idx)
        if i == -1: break
        if i > 0: idx = i

        # text[idx] == '{', now find matching '}'
        if text.startswith('{}', idx):
            string_info.add_string_command(None, '', errors, lnum)
            idx = idx + 2
            continue

        if text.startswith('{{}', idx):
            string_info.add_string_command(None, '{', errors, lnum)
            idx = idx + 3
            continue

        m = param_pat.match(text, idx)
        if m:
            if m.group(1) is None:
                argnum = None
            else:
                argnum = int(m.group(1)[:-1], 10)

            entry = PARAMETERS.get(m.group(2))
            if entry is None or entry.takes_param == 0:
                if argnum is not None:
                    errors.append((ERROR, lnum, "String command {} does not take an argument count".format(m.group(2))))
                    return None

            if entry is None:
                if extra_commands is None: # Allow any additional command.
                    string_info.extra_commands.add(m.group(2))
                elif m.group(2) not in extra_commands: # Verify against set of supplied extra commands.
                    errors.append((ERROR, lnum, "Unknown string command {} found".format("{" + m.group(2) + "}")))
                    return None

            if entry is None or entry.takes_param == 0:
                string_info.add_string_command(None, m.group(2), errors, lnum)
            else:
                if argnum is not None: pos = argnum
                string_info.add_string_command(pos, m.group(2), errors, lnum)
                pos = pos + 1

            idx = m.end()
            continue

        if text.startswith('{P ', idx):
            args = get_arguments(text, lnum, 'P', idx + 2, errors)
            if args is None: return None

            args, idx = args
            expected = plural_count
            num = None
            if expected == 0:
                errors.append((ERROR, lnum, "{P ..} cannot be used without defining the plural type with ##plural"))
                return None
            elif len(args) == expected:
                num = pos - 1
            elif len(args) == expected + 1:
                # Extra argument, is the first argument a number?
                try:
                    num = int(args[0], 10)
                except ValueError:
                    pass
                    # Fall through to the general error

            if num is None:
                errors.append((ERROR, lnum, "Expected {} string arguments for {{P ..}}, found {} arguments".format(expected, len(args))))
                return None

            string_info.add_plural(num)
            continue


        # {G=...}
        m = gender_assign_pat.match(text, idx)
        if m:
            if idx != 0:
                errors.append((ERROR, lnum, "{} may only be used at the start of a string".format(m.group(0))))
                return None
            if not default_case:
                errors.append((ERROR, lnum, '{G=..} may only be used for the default string (that is, without case extension)'))
                return None
            if m.group(1) not in gender:
                errors.append((ERROR, lnum, "Gender {} is not listed in ##gender".format(m.group(1))))
                return None

            idx = m.end()
            continue

        if text.startswith('{G ', idx):
            assert text[idx:idx+2] != '{G='
            args = get_arguments(text, lnum, 'G', idx + 2, errors)
            if args is None: return None

            args, idx = args
            expected = len(gender)
            num = None
            if expected == 0:
                errors.append((ERROR, lnum, "{G ..} cannot be used without defining the genders with ##gender"))
                return None
            elif len(args) == expected:
                num = pos
            elif len(args) == expected + 1:
                # Extra argument, is the first argument a number?
                try:
                    num = int(args[0], 10)
                except ValueError:
                    pass
                    # Fall through to the general error

            if num is None:
                errors.append((ERROR, lnum, "Expected {} string arguments for {{G ..}}, found {} arguments".format(expected, len(args))))
                return None

            string_info.add_gender(num)
            continue


        errors.append((ERROR, lnum, "Unknown {...} command found in the string"))
        return None

    if string_info.check_sanity(errors, lnum): return string_info
    return None

# {{{ def get_arguments(text, lnum, cmd, idx, errors):
def get_arguments(text, lnum, cmd, idx, errors):
    """
    Get arguments of a C{"{P"} or C{"{G"}.

    @param text: String text.
    @type  text: C{str}

    @param lnum: Line number (0-based)
    @type  lnum: C{int} or C{None}

    @param cmd: Command being parsed ('P' or 'G').
    @type  cmd: C{str}

    @param idx: Index in the text to start searching.
    @type  idx: C{int}

    @param errors: Errors found so far, list of line numbers + message.
    @type  errors: C{list} of ((C{int} or C{None}), C{str})

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
            arg = m.group(1)
            if arg[0] == '"' and arg[1] == '"': # Strip quotes
                arg = arg[1:-1]
            args.append(arg)
            idx = m.end()
            continue

        errors.append((ERROR, lnum, "Error while parsing arguments of a '{}' command".format('{' + cmd + '..}')))
        return None

    errors.append((ERROR, lnum, "Missing the terminating '}}' while parsing arguments of a '{}' command".format('{' + cmd + '..}')))
    return None

# }}}
# {{{ class NewGrfStringInfo:
class NewGrfStringInfo:
    """
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
    """
    def __init__(self):
        self.genders  = []
        self.plurals  = []
        self.commands = []
        self.non_positionals = {}
        self.extra_commands = set()

    def __str__(self):
        rv = []
        if len(self.genders) > 0: rv.append("gender=" + str(self.genders))
        if len(self.plurals) > 0: rv.append("plural=" + str(self.plurals))
        if len(self.commands) > 0: rv.append("commands=" + str(self.commands))
        if len(self.non_positionals) > 0: rv.append("non-pos=" + str(self.non_positionals))
        if len(self.extra_commands) > 0: rv.append("extra=" + str(self.extra_commands))
        return "**strinfo(" + ", ".join(rv) + ")"

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

    def add_string_command(self, pos, cmd, errors, lnum):
        """
        Add a string command at the stated position.

        @param pos: String parameter number if required (else C{None}.
        @type  pos: C{int}, or C{None}

        @param cmd: String command used at the stated position.
        @type  cmd: C{str}

        @param errors: Errors found so far, list of line numbers + message.
        @type  errors: C{list} of ((C{ERROR} or C{WARNING}, C{int} or C{None}), C{str})

        @return: Whether the command was correct.
        @rtype:  C{bool}
        """
        if pos is None:
            cnt = self.non_positionals.get(cmd, 0)
            self.non_positionals[cmd] = cnt + 1
            return True

        if pos < len(self.commands):
            if self.commands[pos] != cmd:
                errors.append((ERROR, lnum, "String parameter {} has more than one string command".format(pos)))
                return False
            return True
        while pos > len(self.commands): self.commands.append(None)
        self.commands.append(cmd)
        return True

    def check_sanity(self, errors, lnum):
        """
        Check sanity of the string commands and parameters.

        @param errors: Errors found so far, list of line numbers + message.
        @type  errors: C{list} of ((C{ERROR} or C{WARNING}, C{int} or C{None}), C{str})

        @param lnum: Line number (0-based).
        @type  lnum: C{int}

        @return: Whether the string parameters and commands are correct.
        @rtype:  C{bool}
        """
        ok = True
        for pos, cmd in enumerate(self.commands):
            if cmd is None:
                errors.append((ERROR, lnum, "String parameter {} has no string command".format(pos)))
                ok = False
        if ok:
            for pos in self.plurals:
                if pos < 0 or pos >= len(self.commands):
                    errors.append((ERROR, lnum, "String parameter {} is out of bounds for plural queries {{P ..}}".format(pos)))
                    ok = False
                    continue

                parm = PARAMETERS[self.commands[pos]]
                if not parm.use_plural:
                    errors.append((ERROR, lnum, "String parameter {} may not be used for plural queries {{P ..}}".format(pos)))
                    ok = False

        if ok:
            for pos in self.genders:
                if pos < 0 or pos >= len(self.commands):
                    errors.append((ERROR, lnum, "String parameter {} is out of bounds for gender queries {{G ..}}".format(pos)))
                    ok = False
                    continue

                parm = PARAMETERS[self.commands[pos]]
                if not parm.use_gender:
                    errors.append((ERROR, lnum, "String parameter {} may not be used for gender queries {{P ..}}".format(pos)))
                    ok = False

        return ok

# }}}
# {{{ PARAMETERS
ParameterInfo = collections.namedtuple('ParameterInfo', 'literal takes_param use_plural use_gender')

_PARAMETERS = [
    ParameterInfo("NBSP",           False, False, False),
    ParameterInfo("COPYRIGHT",      False, False, False),
    ParameterInfo("TRAIN",          False, False, False),
    ParameterInfo("LORRY",          False, False, False),
    ParameterInfo("BUS",            False, False, False),
    ParameterInfo("PLANE",          False, False, False),
    ParameterInfo("SHIP",           False, False, False),
    ParameterInfo("TINYFONT",       False, False, False),
    ParameterInfo("BIGFONT",        False, False, False),
    ParameterInfo("BLUE",           False, False, False),
    ParameterInfo("SILVER",         False, False, False),
    ParameterInfo("GOLD",           False, False, False),
    ParameterInfo("RED",            False, False, False),
    ParameterInfo("PURPLE",         False, False, False),
    ParameterInfo("LTBROWN",        False, False, False),
    ParameterInfo("ORANGE",         False, False, False),
    ParameterInfo("GREEN",          False, False, False),
    ParameterInfo("YELLOW",         False, False, False),
    ParameterInfo("DKGREEN",        False, False, False),
    ParameterInfo("CREAM",          False, False, False),
    ParameterInfo("BROWN",          False, False, False),
    ParameterInfo("WHITE",          False, False, False),
    ParameterInfo("LTBLUE",         False, False, False),
    ParameterInfo("GRAY",           False, False, False),
    ParameterInfo("DKBLUE",         False, False, False),
    ParameterInfo("BLACK",          False, False, False),

    ParameterInfo("COMMA",          True,  True,  False),
    ParameterInfo("SIGNED_WORD",    True,  True,  False),
    ParameterInfo("UNSIGNED_WORD",  True,  True,  False),
    ParameterInfo("CURRENCY",       True,  False, False),
    ParameterInfo("VELOCITY",       True,  False, False),
    ParameterInfo("VOLUME",         True,  False, False),
    ParameterInfo("VOLUME_SHORT",   True,  False, False),
    ParameterInfo("POWER",          True,  False, False),
    ParameterInfo("WEIGHT",         True,  False, False),
    ParameterInfo("WEIGHT_SHORT",   True,  False, False),
    ParameterInfo("HEX",            True,  False, False),
    ParameterInfo("STRING",         True,  False, True ),
    ParameterInfo("DATE1920_LONG",  True,  False, False),
    ParameterInfo("DATE1920_SHORT", True,  False, False),
    ParameterInfo("DATE_LONG",      True,  False, False),
    ParameterInfo("DATE_SHORT",     True,  False, False),
    ParameterInfo("POP_WORD",       True,  False, False),
    ParameterInfo("STATION",        True,  False, False),
]

PARAMETERS = dict((x.literal, x) for x in _PARAMETERS)

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
    @type case: C{str} or C{None}

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
                    - 'literal'   Line literally copied
                    - 'string'    Line with a text string (possibly many when there are cases)
                    - 'grflangid' Line with the language id
                    - 'plural'    Plural number
                    - 'case'      Cases line
                    - 'gender'    Gender line

    @ivar strings: Strings with their line number, name and text.
    @type strings: C{list} of L{StringValue}
    """
    def __init__(self):
        self.grflangid = None
        self.language_data = None
        self.plural = None
        self.gender = []
        self.case = []
        self.skeleton = []
        self.strings = []

    def cleanup_skeleton(self):
        """
        Clean up the skeleton file, and ensure it has all language properties.
        """
        while len(self.skeleton) > 0 and self.skeleton[0][0] == 'literal' and self.skeleton[0][1] == '': del self.skeleton[0]
        while len(self.skeleton) > 0 and self.skeleton[-1][0] == 'literal' and self.skeleton[-1][1] == '': del self.skeleton[-1]

# }}}

def get_plural_count(plural):
    """
    Get the number of plural forms to expect in a {P ..}.

    @param plural: The plural number.
    @type  plural: C{int}, or C{None} for no plurals.

    @return: Number of plural forms to expect in a {P ..}.
    @rtype:  C{int}
    """
    if plural is None:
        return 0
    return num_plurals[plural]

# {{{ def load_language_file(handle, max_size, errors):
# {{{ def handle_pragma(lnum, line, data, errors):
def handle_pragma(lnum, line, data, errors):
    """
    Handle a pragma line.

    @param lnum: Line number (0-based).
    @type  lnum: C{int}

    @param line: Text of the line.
    @type  line: C{str}

    @param data: Data store of the properties.
    @type  data: L{NewGrfData}

    @param errors: Errors found so far, list of line numbers + message.
    @type  errors: C{list} of ((C{int} or C{None}), C{str})
    """
    line = line.split()
    if line[0] == '##grflangid':
        if len(line) != 2:
            errors.append((ERROR, lnum, "##grflangid takes exactly one argument"))
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
            errors.append((ERROR, lnum, "##grflangid is neither a valid language name nor a language code"))
            return
        for entry in language_info.all_languages:
            if entry.grflangid == val:
                data.grflangid = val
                data.language_data = entry
                return
        # Don't know what it is.
        errors.append((ERROR, lnum, "##grflangid is neither a valid language name nor a language code"))
        return

    if line[0] == '##plural':
        if len(line) != 2:
            errors.append((ERROR, lnum, "##plural takes exactly one numeric argument in the range 0..12"))
            return
        try:
            val = int(line[1], 10)
        except ValueError:
            val = -1
        if val < 0 or val > 12:
            errors.append((ERROR, lnum, "##plural takes exactly one numeric argument in the range 0..12"))
            return
        data.plural = val
        return

    if line[0] == '##gender':
        if len(line) == 1:
            errors.append((ERROR, lnum, "##gender takes a non-empty list of gender names"))
            return
        data.gender = line[1:]
        return

    if line[0] == '##case':
        if len(line) == 1:
            errors.append((ERROR, lnum, "##case takes a non-empty list of case names"))
            return
        data.case = line[1:]
        return

    errors.append((ERROR, lnum, "Unknown pragma '{}'".format(line[0])))
    return
# }}}

string_pat = re.compile('^([A-Za-z_0-9]+)(.[A-Za-z0-9]+)?[ \\t]*:(.*)$')
bom = codecs.BOM_UTF8.decode('utf-8')

def load_language_file(handle, max_size, errors):
    """
    Load a language file.

    @param handle: File handle.
    @type  handle: L{io.BufferedReader}

    @param max_size: Maimum allowed size to read from the handle.
    @type  max_size: C{int}

    @param errors: Problems found while parsing the file. Extended in-place.
    @type  errors: C{list} of triples (C{WARNING} or C{ERROR}, {cint} or C{None}, C{string})

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
    data.skeleton.append(('literal', ''))

    # Read file, and process the lines.
    text = handle.read(max_size)
    if len(text) == max_size: errors.append((ERROR, None, 'File not completely read'))
    text = str(text, encoding = "utf-8")
    for lnum, line in enumerate(text.split('\n')):
        line = line.rstrip()
        if line.startswith(bom):
            line = line[len(bom):]

        if line.startswith('##'):
            if seen_strings:
                errors.append((ERROR, lnum, "Cannot change language properties after processing strings"))
                continue
            handle_pragma(lnum, line, data, errors)
            continue

        if line == "" or line.startswith(';') or line.startswith('#'):
            data.skeleton.append(('literal', line))
            continue

        m = string_pat.match(line) # Regular string line?
        if m:
            seen_strings = True # Disable processing of ## pragma lines
            if m.group(2) is None:
                m2 = None
            else:
                m2 = m.group(2)[1:]
            sv = StringValue(lnum, m.group(1), m2, m.group(3))
            data.strings.append(sv)
            if m2 is None:
                if m.group(1) in skeleton_strings:
                    errors.append((ERROR, lnum, 'String name {} is already used.'.format(m.group(1))))
                    continue
                skeleton_strings.add(m.group(1))
                data.skeleton.append(('string', m.group(1)))
            continue

        errors.append((ERROR, lnum, "Line not recognized"))

    for sv in data.strings:
        if sv.name not in skeleton_strings:
            errors.append((ERROR, None, 'String name \"{}\" has no default definition (that is, without case).'.format(sv.name)))

    if data.language_data is None:
        errors.append((ERROR, None, 'Language file has no ##grflangid'))

    data.cleanup_skeleton()
    return data

# }}}

def get_base_string_info(text, lng, errors):
    """
    Get the information about the used parameters from a string in the base language.

    @param text: String to examine.
    @type  text: C{str}

    @param lng: Language containing the string.
    @type  lng: L{Language}

    @param errors: Errors found in the string are appended to this list.
    @type  errors: C{list} of (C{str}, C{int} or C{None}, C{str})

    @return: Information about the used string parameters.
    @rtype:  L{NewGrfStringInfo}
    """
    return check_string(text, None, True, None, get_plural_count(lng.plural), lng.gender, errors)

def get_translation_string_info(text, case, extra_commands, lng, errors):
    """
    Get the information about the used parameters from a string in a translation.

    @param text: String to examine.
    @type  text: C{str}

    @param case: Case of the string, if given.
    @type  case: C{str} or C{None}

    @param extra_commands: Extra commands that are allowed in the translation.
    @type  extra_commands: C{set} of C{str}

    @param lng: Language containing the string.
    @type  lng: L{Language}

    @param errors: Errors found in the string are appended to this list.
    @type  errors: C{list} of (C{str}, C{int} or C{None}, C{str})

    @return: Information about the used string parameters.
    @rtype:  L{NewGrfStringInfo}
    """
    return check_string(text, None, case is None, extra_commands, get_plural_count(lng.plural), lng.gender, errors)

def compare_info(base_info, lng_info):
    """
    Compare both string uses with each other.

    @param base_info: Information about string parameters from the base language.
    @type  base_info: L{NewGrfStringInfo}

    @param lng_info: Information about string parameters from the translation.
    @type  lng_info: L{NewGrfStringInfo}

    @return: Whether both parameter uses are compatible.
    @rtype:  C{bool}
    """
    if base_info is None: return True # Cannot blame the translation when the base language is broken.
    if lng_info is None: return False # Translation has more serious problems.

    if base_info.commands != lng_info.commands: return False # Positional commands must match precisely.

    # Non-positional commands must match in count only.
    if len(base_info.non_positionals) != len(lng_info.non_positionals): return False
    for bname, bcnt in base_info.non_positionals.items():
        lcnt = lng_info.non_positionals.get(bname)
        if lcnt is None or lcnt != bcnt: return False

    return True

