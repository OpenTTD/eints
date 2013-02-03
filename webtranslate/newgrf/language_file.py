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

    def get_arguments(self, cmd, idx, errors):
        """
        Get arguments of a C{"{P"} or C{"{G"}.

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
        while idx < len(self.text):
            m = end_argument_pat.match(self.text, idx)
            if m:
                return args, m.end()
            m = argument_pat.match(self.text, idx)
            if m:
                arg = m.group(1)
                if arg[0] == '"' and arg[1] == '"': # Strip quotes
                    arg = arg[1:-1]
                args.append(arg)
                idx = m.end()
                continue

            errors.append((ERROR, self.lnum, "Error while parsing arguments of a '{}' command".format('{' + cmd + '..}')))
            return None

        errors.append((ERROR, self.lnum, "Missing the terminating '}}' while parsing arguments of a '{}' command".format('{' + cmd + '..}')))
        return None


    def check_string(self, data, errors):
        """
        Check the contents of a single string.

        @param data: Language properties.
        @param errors: Errors found so far, list of line numbers + message.
        @type  errors: C{list} of ((C{ERROR} or C{WARNING}, C{int} or C{None}), C{str})

        @return: Whether the string was correct.
        @rtype:  C{bool}
        """
        idx = 0
        while idx < len(self.text):
            i = self.text.find('{', idx)
            if i == -1:
                return True
            if i > 0:
                idx = i

            # self.text[idx] == '{', now find matching '}'
            if self.text.startswith('{}', idx):
                idx = idx + 2
                continue

            if self.text.startswith('{{}', idx):
                idx = idx + 3
                continue

            m = param_pat.match(self.text, idx)
            if m:
                if m.group(1) is None:
                    argnum = None
                else:
                    argnum = int(m.group(1)[:-1], 10)

                found = False
                entry = PARAMETERS.get(m.group(2))
                if entry is not None:
                    if entry.arg_count == 0 and argnum is not None:
                        errors.append((ERROR, self.lnum, "String parameter {} does not take an argument count".format(entry.literal)))
                        return

                # XXX Check sanity of argnum

                idx = m.end()
                continue

            if self.text.startswith('{P', idx):
                args = self.get_arguments('P', idx + 2, errors)
                if args is None:
                    return False
                args, idx = args
                expected = data.get_plural_count()
                # XXX Check sanity of argument number
                if expected == 0:
                    errors.append((ERROR, self.lnum, "{P ..} cannot be used without defining the plural type with ##plural"))
                    return False
                if len(args) == expected:
                    continue
                if len(args) == expected + 1:
                    # Extra argument, is the first argument a number?
                    try:
                        num = int(args[0], 10)
                        continue # Yep, all is fine.
                    except ValueError:
                        pass
                        # Fall through to the general error

                errors.append((ERROR, self.lnum, "Expected {} string arguments for {P ..}, found {} arguments".format(expected, len(args))))
                return False


            # {G=...}
            m = gender_assign_pat.match(self.text, idx)
            if m:
                if idx != 0:
                    errors.append((ERROR, self.lnum, "{} may only be used at the start of a string".format(m.group(0))))
                    return False
                if self.case is not None:
                    errors.append((ERROR, self.lnum, '{G=..} may only be used for the default string (that is, without case extension)'))
                    return False
                if m.group(1) not in data.gender:
                    errors.append((ERROR, self.lnum, "Gender {} is not listed in ##gender".format(m.group(1))))
                    return False

                idx = m.end()
                continue

            if self.text.startswith('{G', idx):
                assert self.text[idx:idx+2] != '{G='
                args = self.get_arguments('G', idx + 2, errors)
                if args is None:
                    return False
                args, idx = args
                expected = len(data.gender)
                if expected == 0:
                    errors.append((ERROR, self.lnum, "{G ..} cannot be used without defining the genders with ##gender"))
                    return False
                if len(args) == expected:
                    continue
                if len(args) == expected + 1:
                    # Extra argument, is the first argument a number?
                    try:
                        num = int(args[0], 10)
                        continue # Yep, all is fine.
                    except ValueError:
                        pass
                        # Fall through to the general error

                errors.append((ERROR, self.lnum, "Expected {} string arguments for {G ..}, found {} arguments".format(expected, len(args))))
                return False


            errors.append((ERROR, self.lnum, "Unknown {...} command found in the string"))
            return False


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

    def get_plural_count(self):
        """
        Get the number of plural forms to expect in a {P ..}.

        @return: Number of plural forms to expect in a {P ..}.
        @rtype:  C{int}
        """
        if self.plural is None:
            return 0
        return num_plurals[self.plural]

def handle_pragma(lnum, line, data, errors):
    """
    Handle a pragma line.

    @param lnum: Line number (0-based).
    @type  lnum: C{int}

    @param line: Text of the line.
    @type  line: C{str}

    @param data: Data store of the properties.
    @type  data: L{NewgrfData}

    @param errors: Errors found so far, list of line numbers + message.
    @type  errors: C{list} of ((C{int} or C{None}), C{str})
    """
    line = line.split()
    if line[0] == '##grflangid':
        data.skeleton.append(('grflangid', ''))

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
        data.skeleton.append(('plural', ''))

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
        data.skeleton.append(('gender', ''))

        if len(line) == 1:
            errors.append((ERROR, lnum, "##gender takes a non-empty list of gender names"))
            return
        data.gender = line[1:]
        return

    if line[0] == '##case':
        data.skeleton.append(('case', ''))

        if len(line) == 1:
            errors.append((ERROR, lnum, "##case takes a non-empty list of case names"))
            return
        data.case = line[1:]
        return

    errors.append((ERROR, lnum, "Unknown pragma '{}'".format(line[0])))
    return


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
            sv.check_string(data, errors)
            continue

        errors.append((ERROR, lnum, "Line not recognized"))

    for sv in data.strings:
        if sv.name not in skeleton_strings:
            errors.append((ERROR, None, 'String name \"{}\" has no default definition (that is, without case).'.format(sv.name)))

    if data.language_data is None:
        errors.append((ERROR, None, 'Language file has no ##grflangid'))

    return data

ParameterInfo = collections.namedtuple('ParameterInfo', 'literal arg_count')

_PARAMETERS = [
    ParameterInfo("NBSP",           0),
    ParameterInfo("COPYRIGHT",      0),
    ParameterInfo("TRAIN",          0),
    ParameterInfo("LORRY",          0),
    ParameterInfo("BUS",            0),
    ParameterInfo("PLANE",          0),
    ParameterInfo("SHIP",           0),
    ParameterInfo("TINYFONT",       0),
    ParameterInfo("BIGFONT",        0),
    ParameterInfo("BLUE",           0),
    ParameterInfo("SILVER",         0),
    ParameterInfo("GOLD",           0),
    ParameterInfo("RED",            0),
    ParameterInfo("PURPLE",         0),
    ParameterInfo("LTBROWN",        0),
    ParameterInfo("ORANGE",         0),
    ParameterInfo("GREEN",          0),
    ParameterInfo("YELLOW",         0),
    ParameterInfo("DKGREEN",        0),
    ParameterInfo("CREAM",          0),
    ParameterInfo("BROWN",          0),
    ParameterInfo("WHITE",          0),
    ParameterInfo("LTBLUE",         0),
    ParameterInfo("GRAY",           0),
    ParameterInfo("DKBLUE",         0),
    ParameterInfo("BLACK",          0),

    ParameterInfo("COMMA",          1),
    ParameterInfo("SIGNED_WORD",    1),
    ParameterInfo("UNSIGNED_WORD",  1),
    ParameterInfo("CURRENCY",       1),
    ParameterInfo("VELOCITY",       1),
    ParameterInfo("VOLUME",         1),
    ParameterInfo("VOLUME_SHORT",   1),
    ParameterInfo("POWER",          1),
    ParameterInfo("WEIGHT",         1),
    ParameterInfo("WEIGHT_SHORT",   1),
    ParameterInfo("HEX",            1),
    ParameterInfo("STRING",         1),
    ParameterInfo("DATE1920_LONG",  1),
    ParameterInfo("DATE1920_SHORT", 1),
    ParameterInfo("DATE_LONG",      1),
    ParameterInfo("DATE_SHORT",     1),
    ParameterInfo("POP_WORD",       1),
    ParameterInfo("STATION",        1),
]

PARAMETERS = dict((x.literal, x) for x in _PARAMETERS)
