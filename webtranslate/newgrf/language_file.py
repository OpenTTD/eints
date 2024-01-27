"""
Language file processing.
"""

import codecs
import re

from ..parameter_info_table import (
    CURLY_PARAMETER,
    NL_PARAMETER,
)
from ..newgrf import language_info

ERROR = "Error"
WARNING = "Warning"


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


param_pat = re.compile("{([0-9]+:)?([A-Z_0-9]+)(\\.[A-Za-z0-9]+)?}")
gender_assign_pat = re.compile("{G *= *([^ }]+) *}")
argument_pat = re.compile('[ \\t]+([^"][^ \\t}]*|"[^"}]*")')
end_argument_pat = re.compile("[ \\t]*}")
posref_pat = re.compile("([0-9]+)(:([0-9]+))?$")


def check_string(projtype, text, default_case, extra_commands, lng, in_blng, save_pieces=False):
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

    @param in_blng: Whether the string is in the base language.
    @type  in_blng: C{bool}

    @param save_pieces: Save the pieces of the string for translation string construction.
    @type  save_pieces: C{bool}

    @return: String parameter information.
    @rtype:  C{StringInfo}
    """
    assert projtype.allow_gender or len(lng.gender) == 0
    assert projtype.allow_case or default_case

    if not projtype.allow_extra:
        extra_commands = set()
    string_info = StringInfo(extra_commands, in_blng, save_pieces)
    plural_count = language_info.all_plurals[lng.plural].count

    pos = 0  # String parameter number.
    idx = 0  # Text string index.
    while idx < len(text):
        i = text.find("{", idx)
        if i == -1:
            if save_pieces:
                string_info.add_text(text[idx:])
            break
        if i > idx:
            if save_pieces:
                string_info.add_text(text[idx:i])
            idx = i

        # text[idx] == '{', now find matching '}'
        if text.startswith("{}", idx):
            string_info.add_nonpositional(NL_PARAMETER)
            idx = idx + 2
            continue

        if text.startswith("{{}", idx):
            string_info.add_nonpositional(CURLY_PARAMETER)
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
                    string_info.add_error(
                        ERROR, None, "String command {} does not take an argument count".format(m.group(2))
                    )
                    return string_info
                if case is not None:
                    string_info.add_error(ERROR, None, "String command {} does not take a case".format(m.group(2)))
                    return string_info

                if not string_info.add_extra_command(m.group(2)):
                    return string_info
                idx = m.end()
                continue

            if case is not None:
                if not projtype.allow_case:
                    string_info.add_error(
                        ERROR,
                        None,
                        "Case detected in string command {} but the project does not allow cases".format(m.group(2)),
                    )
                    return string_info
                if not entry.allow_case:
                    string_info.add_error(ERROR, None, "String command {} does not take a case".format(m.group(2)))
                    return string_info
                if case not in lng.case:
                    string_info.add_error(
                        ERROR,
                        None,
                        "Case {} of string command {} does not exist in the language".format(case, m.group(2)),
                    )
                    return string_info

            if len(entry.parameters) == 0:
                if argnum is not None:
                    string_info.add_error(
                        ERROR, None, "String command {} does not take an argument count".format(m.group(2))
                    )
                    return string_info

                string_info.add_nonpositional(entry)
            else:
                if argnum is not None:
                    pos = argnum
                string_info.add_positional(pos, argnum, entry, case)
                pos = pos + 1

            idx = m.end()
            continue

        if text.startswith("{P ", idx):
            args = get_arguments(text, "P", idx + 2, string_info)
            if args is None:
                return string_info

            args, idx = args
            if plural_count == 0:
                string_info.add_error(
                    ERROR, None, "{P ..} cannot be used without defining the plural type with ##plural"
                )
                return string_info
            elif len(args) > 0:
                # If the first argument is a number, it cannot be a value for the plural command.
                m = posref_pat.match(args[0])
                if m:
                    num = int(m.group(1), 10)
                    sub = m.group(3)

                    if sub is not None:
                        sub = int(sub, 10)

                    num = cmd_num = (num, sub)

                    cmd_args = args[1:]
                else:
                    num = (pos - 1, None)
                    cmd_num = (None, None)
                    cmd_args = args

                if len(cmd_args) == plural_count:
                    string_info.add_plural(num, cmd_num, cmd_args)
                    continue

            string_info.add_error(
                ERROR,
                None,
                "Expected {} string arguments for {{P ..}}, found {} arguments".format(plural_count, len(args)),
            )
            return string_info

        # {G=...}
        m = gender_assign_pat.match(text, idx)
        if m:
            if not projtype.allow_gender:
                string_info.add_error(ERROR, None, "{G=..} detected, but the project does not support genders")
                return string_info
            if idx != 0:
                string_info.add_error(ERROR, None, "{} may only be used at the start of a string".format(m.group(0)))
                return string_info
            if not default_case:
                string_info.add_error(
                    ERROR, None, "{G=..} may only be used for the default string (that is, without case extension)"
                )
                return string_info
            if m.group(1) not in lng.gender:
                string_info.add_error(ERROR, None, "Gender {} is not listed in ##gender".format(m.group(1)))
                return string_info

            if save_pieces:
                string_info.add_gender_assignment(m.group(1))
            idx = m.end()
            continue

        if text.startswith("{G ", idx):
            if not projtype.allow_gender:
                string_info.add_error(ERROR, None, "{G ..} detected, but the project does not support genders")
                return string_info

            args = get_arguments(text, "G", idx + 2, string_info)
            if args is None:
                return string_info

            args, idx = args
            expected = len(lng.gender)
            if expected == 0:
                string_info.add_error(ERROR, None, "{G ..} cannot be used without defining the genders with ##gender")
                return string_info
            elif len(args) > 0:
                # If the first argument is a number, it cannot be a value for the plural command.
                m = posref_pat.match(args[0])
                if m:
                    num = int(m.group(1), 10)
                    sub = m.group(3)

                    if sub is None:
                        cmd_num = (num, None)
                        num = (num, 0)
                    else:
                        sub = int(sub, 10)
                        num = cmd_num = (num, sub)

                    cmd_args = args[1:]
                else:
                    num = (pos, 0)
                    cmd_num = (None, None)
                    cmd_args = args

                if len(cmd_args) == expected:
                    string_info.add_gender(num, cmd_num, cmd_args)
                    continue

            string_info.add_error(
                ERROR,
                None,
                "Expected {} string arguments for {{G ..}}, found {} arguments".format(expected, len(args)),
            )
            return string_info

        string_info.add_error(ERROR, None, "Unknown {...} command found in the string")
        return string_info

    if in_blng:
        string_info.check_plural_and_gender(string_info)

    return string_info


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
    @type  string_info: L{StringInfo}

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
            args.append(m.group(1))  # Do not strip quotes to keep the difference between {P 0 ..} and {P "0" ..}.
            idx = m.end()
            continue

        string_info.add_error(ERROR, None, "Error while parsing arguments of a '{}' command".format("{" + cmd + "..}"))
        return None

    string_info.add_error(
        ERROR,
        None,
        "Missing the terminating '}}' while parsing arguments of a '{}' command".format("{" + cmd + "..}"),
    )
    return None


class StringPiece:
    """
    Base class for storing a piece of the string.
    """

    def get_translation_text(self):
        """
        Return the text of the piece (in the base language) as it should be displayed for translating.

        @return: Text to display to the user for translating.
        @rtype:  C{str}
        """
        raise NotImplementedError("Implement me in " + repr(self))


class TextPiece(StringPiece):
    """
    Piece representing literal text from the string.

    @ivar text: Literal text.
    @type text: C{str}
    """

    def __init__(self, text):
        self.text = text

    def get_translation_text(self):
        return self.text


class CmdPiece(StringPiece):
    """
    Piece representing a string command.

    @ivar argnum: Argument number, if provided.
    @type argnum: C{int} or C{None}

    @ivar cmd: Command.
    @type cmd: L{ParameterInfo}

    @ivar case: Case suffix, if provided.
    @type case: C{str} or C{None}
    """

    def __init__(self, argnum, cmd, case):
        self.argnum = argnum
        self.cmd = cmd
        self.case = case

    def get_translation_text(self):
        if self.argnum is None and self.case is None and self.cmd.translated_cmd is None:
            # Do common case quickly.
            return "{" + self.cmd.literal + "}"

        parts = ["{"]
        if self.argnum is not None:
            parts.append(str(self.argnum))
            parts.append(":")
        if self.cmd.translated_cmd is None:
            parts.append(self.cmd.literal)
        else:
            parts.append(self.cmd.translated_cmd)
        if self.case is not None:
            parts.append(".")
            parts.append(self.case)
        parts.append("}")
        return "".join(parts)


class ExtraCmdPiece(StringPiece):
    """
    Piece representing an extra command.

    @ivar text: Text of the extra command.
    @type text: C{str}
    """

    def __init__(self, text):
        self.text = text

    def get_translation_text(self):
        return "{" + self.text + "}"


class PluralPiece(StringPiece):
    """
    Piece representing a plural {P ...} command.

    @param cmd_num: Number given to the command by the user, if provided.
    @type  cmd_num: C{pair} of (C{int} or C{None})

    @ivar cmd_args: Plural command arguments.
    @type cmd_args: C{list} of C{str}
    """

    def __init__(self, cmd_num, cmd_args):
        self.cmd_args = cmd_args
        self.cmd_num = cmd_num

    def get_translation_text(self):
        prefix = "{P "
        if self.cmd_num[0] is not None:
            prefix += str(self.cmd_num[0])
            if self.cmd_num[1] is not None:
                prefix += ":" + str(self.cmd_num[1])
            prefix += " "
        return prefix + " ".join(self.cmd_args) + "}"


class GenderPiece(StringPiece):
    """
    Piece representing a gender {G ...} command.

    @param cmd_num: Number given to the command by the user, if provided.
    @type  cmd_num: C{pair} of (C{int} or C{None})

    @ivar cmd_args: Gender command arguments.
    @type cmd_args: C{list} of C{str}
    """

    def __init__(self, cmd_num, cmd_args):
        self.cmd_args = cmd_args
        self.cmd_num = cmd_num

    def get_translation_text(self):
        prefix = "{G "
        if self.cmd_num[0] is not None:
            prefix += str(self.cmd_num[0])
            if self.cmd_num[1] is not None:
                prefix += ":" + str(self.cmd_num[1])
            prefix += " "
        return prefix + " ".join(self.cmd_args) + "}"


class GenderAssignPiece(StringPiece):
    """
    Piece representing a gender assignment command.

    @ivar gender: Gender of the assignment.
    @type gender: C{str}
    """

    def __init__(self, gender):
        self.gender = gender

    def get_translation_text(self):
        return "{G=" + self.gender + "}"


class StringInfo:
    """
    Collected information about a string.

    @ivar allowed_extra: Extra commands that are allowed, if supplied.
    @type allowed_extra: C{None} if any extra commands are allowed,
                         C{set} of C{str} if a specific set of extra commands is allowed.

    @ivar in_blng: Whether the parsed string is from the base language.
    @type in_blng: C{bool}

    @ivar genders: String parameter numbers used for gender queries.
    @type genders: C{list} of C{int}

    @ivar plurals: String parameter numbers used for plural queries.
    @type plurals: C{list} of C{int}

    @ivar commands: String commands at each position.
    @type commands: C{list} of (L{ParameterInfo} or C{None})

    @ivar non_positionals: Mapping of commands without position to their count.
    @type non_positionals: C{dict} of C{str} to C{int}

    @ivar extra_commands: Found extra commands.
    @type extra_commands: C{set} of C{str}

    @ivar errors: Detected errors in the string.
    @type errors: c{list} of L{ErrorMessage}

    @ivar has_error: Whether the L{errors} list has a real error.
    @type has_error: C{bool}

    @ivar pieces: Pieces of the string, for translation string construction, if available.
    @type pieces: C{None} if no pieces available, else a C{list} of L{StringPiece}
    """

    def __init__(self, allowed_extra, in_blng, save_pieces):
        self.in_blng = in_blng
        self.allowed_extra = allowed_extra
        self.genders = []
        self.plurals = []
        self.commands = []
        self.non_positionals = {}
        self.extra_commands = set()
        self.errors = []
        self.has_error = False
        if save_pieces:
            self.pieces = []
        else:
            self.pieces = None

    def __str__(self):
        rv = []
        if len(self.genders) > 0:
            rv.append("gender=" + str(self.genders))
        if len(self.plurals) > 0:
            rv.append("plural=" + str(self.plurals))
        if len(self.commands) > 0:
            rv.append("commands=" + str(self.commands))
        if len(self.non_positionals) > 0:
            rv.append("non-pos=" + str(self.non_positionals))
        if len(self.extra_commands) > 0:
            rv.append("extra=" + str(self.extra_commands))
        return "**strinfo(" + ", ".join(rv) + ")"

    def get_translation_text(self):
        """
        Construct the text to display after translating the string commands to
        their equivalent in the translated languages.

        @precond: The parsed string stored in the object should be from the base language.
        @precond: While parsing, the pieces should have been saved in L{pieces}.

        @return: The text to translate against, in terms of a translation.
        @rtype:  C{str}
        """
        return "".join(pc.get_translation_text() for pc in self.pieces)

    def add_error(self, type, line, msg):
        """
        Add an error/warning to the list of detected errors.

        @param type: Type of message (L{ERROR} or L{WARNING}).
        @type  type: C{str}

        @param line: Line number of the message, if available.
        @type  line: C{int} or C{None}

        @param msg: Human readable error/warning message.
        @type  msg: C{str}
        """
        if type == ERROR:
            self.has_error = True

        self.errors.append(ErrorMessage(type, line, msg))

    def add_text(self, text):
        """
        Save a piece of literal text.

        @param text: Literal text of the string to save.
        @type  text: C{str}
        """
        self.pieces.append(TextPiece(text))

    def add_gender(self, pos, cmd_num, cmd_args):
        """
        Add a gender query for parameter L{pos}.

        @param pos: String parameter number used for gender query.
        @type  pos: (C{int}, C{int})

        @param cmd_num: Number given to the command by the user, if provided.
        @type  cmd_num: C{pair} of (C{int} or C{None})

        @param cmd_args: Command arguments.
        @type  cmd_args: C{list} of C{str}
        """
        if pos not in self.genders:
            self.genders.append(pos)
        if self.pieces is not None:
            self.pieces.append(GenderPiece(cmd_num, cmd_args))

    def add_plural(self, pos, cmd_num, cmd_args):
        """
        Add a plural query for parameter L{pos}.

        @param pos: String parameter number used for plural query.
        @type  pos: (C{int}, C{int} or C{None})

        @param cmd_num: Number given to the command by the user, if provided.
        @type  cmd_num: C{pair} of (C{int} or C{None})

        @param cmd_args: Command arguments.
        @type  cmd_args: C{list} of C{str}
        """
        if pos not in self.plurals:
            self.plurals.append(pos)
        if self.pieces is not None:
            self.pieces.append(PluralPiece(cmd_num, cmd_args))

    def add_nonpositional(self, cmd):
        """
        Add a non-positional string command.

        @param cmd: Command to add.
        @type  cmd: L{ParameterInfo}
        """
        cnt = self.non_positionals.get(cmd.literal, 0)
        self.non_positionals[cmd.literal] = cnt + 1
        if self.pieces is not None:
            self.pieces.append(CmdPiece(None, cmd, None))

    def add_extra_command(self, cmdname):
        """
        Add an extra command (a custom tag). The command is always non-positional.

        @param cmdname: Name of the command.
        @type  cmdname: C{str}

        @return: Whether the command was correct.
        @rtype:  C{bool}
        """
        if self.allowed_extra is None:  # Allow any additional command.
            self.extra_commands.add(cmdname)
        elif cmdname not in self.allowed_extra:
            self.add_error(ERROR, None, "Unknown string command {} found".format("{" + cmdname + "}"))
            return False

        cnt = self.non_positionals.get(cmdname, 0)
        self.non_positionals[cmdname] = cnt + 1
        if self.pieces is not None:
            self.pieces.append(ExtraCmdPiece(cmdname))
        return True

    def add_positional(self, pos, argnum, cmd, case):
        """
        Add a string command at the stated position.

        @param pos: String parameter number.
        @type  pos: C{int}

        @param argnum: Number specified with the string command, if available.
        @type  argnum: C{int} or C{None}

        @param cmd: String command used at the stated position.
        @type  cmd: C{ParameterInfo}

        @param case: Case specified with the string command, if available.
        @type  case: C{str} or C{None}

        @return: Whether the command was correct.
        @rtype:  C{bool}
        """
        if pos < len(self.commands):
            if self.commands[pos] is None:
                self.commands[pos] = cmd
                if self.pieces is not None:
                    self.pieces.append(CmdPiece(argnum, cmd, case))
                return True
            if self.commands[pos] != cmd:  # Reference equality is almost always valid.
                if not self.in_blng or self.commands[pos].get_translation_cmd() != cmd.get_translation_cmd():
                    self.add_error(ERROR, None, "String parameter {} has more than one string command".format(pos))
                    return False
            if self.pieces is not None:
                self.pieces.append(CmdPiece(argnum, cmd, case))
            return True
        while pos > len(self.commands):
            self.commands.append(None)
        self.commands.append(cmd)
        if self.pieces is not None:
            self.pieces.append(CmdPiece(argnum, cmd, case))
        return True

    def add_gender_assignment(self, gender):
        """
        Add a gender assignment command.

        @param gender: Gender being assigned.
        @type  gender: C{str}

        @precond: String pieces should be saved.
        """
        self.pieces.append(GenderAssignPiece(gender))

    def check_plural_and_gender(self, base_info):
        """
        Check plural and gender parameter references.

        Note: The base language is required to know the exact string commands and amount of sub-parameters.

        @param base_info: Information about string parameters from the base language.
        @type  base_info: L{StringInfo}

        @return: True of references are valid.
        @rtype:  C{bool}
        """
        ok = True

        for pos, sub in self.plurals:
            pos_name = str(pos)
            if sub is not None:
                pos_name += ":" + str(sub)

            if pos < 0 or pos >= len(base_info.commands):
                self.add_error(
                    ERROR, None, "String parameter {} is out of bounds for plural queries {{P ..}}".format(pos_name)
                )
                ok = False
                continue

            cmd = base_info.commands[pos]
            if cmd is None:
                self.add_error(
                    ERROR, None, "Plural query {{P ..}} references non-existing parameter {}.".format(pos_name)
                )
                ok = False
                continue

            if sub is None:
                sub = cmd.default_plural_pos
            elif sub < 0 or sub >= len(cmd.parameters):
                self.add_error(
                    ERROR, None, "Plural query {{P ..}} references non-existing parameter {}.".format(pos_name)
                )
                ok = False
                continue

            if sub is None or not cmd.use_plural(sub):
                self.add_error(
                    ERROR, None, "String parameter {} may not be used for plural queries {{P ..}}".format(pos_name)
                )
                ok = False

        for pos, sub in self.genders:
            pos_name = str(pos)
            if sub > 0:
                pos_name += ":" + str(sub)

            if pos < 0 or pos >= len(base_info.commands):
                self.add_error(
                    ERROR, None, "String parameter {} is out of bounds for gender queries {{G ..}}".format(pos_name)
                )
                ok = False
                continue

            cmd = base_info.commands[pos]
            if cmd is None or sub < 0 or sub >= len(cmd.parameters):
                self.add_error(
                    ERROR, None, "Gender query {{G ..}} references non-existing parameter {}.".format(pos_name)
                )
                ok = False
                continue

            if not cmd.use_gender(sub):
                self.add_error(
                    ERROR, None, "String parameter {} may not be used for gender queries {{G ..}}".format(pos_name)
                )
                ok = False

        return ok


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


class NewGrfData:
    """
    Data of a NewGRF language.

    @ivar grflangid: Language number.
    @type grflangid: C{int}

    @ivar language_data: Technical information about the language definition.
    @type language_data: L{LanguageData} or C{None}

    @ivar custom_pragmas: Custom pragmas, which are preserved when uploading languages.
    @type custom_pragmas: C{dict} of C{str} to C{str}

    @ivar plural: Plural type, if specified.
    @type plural: C{int} (key into language_info.all_plurals) or C{None}

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
                     - 'pragma':    Custom pragma with specific name

    @ivar strings: Strings with their line number, name and text.
    @type strings: C{list} of L{StringValue}

    @ivar errors: Errors detected during loading of the file.
    @type errors: C{list} of L{ErrorMessage}
    """

    def __init__(self):
        self.grflangid = None
        self.language_data = None
        self.custom_pragmas = {}
        self.plural = None
        self.gender = []
        self.case = [""]
        self.skeleton = []
        self.strings = []
        self.errors = []

    def set_lang(self, language_data):
        """
        Set the language information.

        @param language_data: Language meta-data.
        @type  language_data: L{LanguageData}
        """
        self.grflangid = language_data.grflangid
        self.language_data = language_data

    def add_error(self, type, line, msg):
        """
        Add an error/warning to the list of detected errors.

        @param type: Type of message (L{ERROR} or L{WARNING}).
        @type  type: C{str}

        @param line: Line number of the message, if available.
        @type  line: C{int} or C{None}

        @param msg: Human readable error/warning message.
        @type  msg: C{str}
        """
        self.errors.append(ErrorMessage(type, line, msg))

    def cleanup_skeleton(self):
        """
        Clean up the skeleton file.
        """
        while len(self.skeleton) > 0 and self.skeleton[0][0] == "literal" and self.skeleton[0][1] == "":
            del self.skeleton[0]
        while len(self.skeleton) > 0 and self.skeleton[-1][0] == "literal" and self.skeleton[-1][1] == "":
            del self.skeleton[-1]


def handle_pragma(projtype, lnum, line, data):
    """
    Handle a pragma line.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param lnum: Line number (0-based).
    @type  lnum: C{int}

    @param line: Text of the line.
    @type  line: C{str}

    @param data: Data store of the properties.
    @type  data: L{NewGrfData}
    """
    line = line.split()
    if line[0] == "##grflangid":
        if not projtype.has_grflangid:
            data.add_error(ERROR, lnum, "##grflangid not allowed by the project type")
            return

        if len(line) != 2:
            data.add_error(ERROR, lnum, "##grflangid takes exactly one argument")
            return

        # Is the argument a known text-name?
        for entry in language_info.all_languages:
            if entry.isocode == line[1]:
                data.skeleton.append(("grflangid", ""))
                data.set_lang(entry)
                return

        # Is it a number?
        try:
            val = int(line[1], 16)
        except ValueError:
            data.add_error(ERROR, lnum, "##grflangid is neither a valid language name nor a language code")
            return
        for entry in language_info.all_languages:
            if entry.grflangid == val:
                data.skeleton.append(("grflangid", ""))
                data.set_lang(entry)
                return
        # Don't know what it is.
        data.add_error(ERROR, lnum, "##grflangid is neither a valid language name nor a language code")
        return

    if line[0] == "##plural":
        if len(line) != 2:
            data.add_error(
                ERROR,
                lnum,
                "##plural takes exactly one numeric argument in the range 0..{}".format(
                    max(p for p in language_info.all_plurals if p is not None)
                ),
            )
            return
        try:
            val = int(line[1], 10)
        except ValueError:
            val = -1
        if val not in language_info.all_plurals:
            data.add_error(
                ERROR,
                lnum,
                "##plural takes exactly one numeric argument in the range 0..{}".format(
                    max(p for p in language_info.all_plurals if p is not None)
                ),
            )
            return
        data.skeleton.append(("plural", ""))
        data.plural = val
        return

    if line[0] == "##gender":
        if not projtype.allow_gender:
            data.add_error(ERROR, lnum, "##gender is not allowed in the project")
            return
        if len(line) == 1:
            data.add_error(ERROR, lnum, "##gender takes a non-empty list of gender names")
            return
        data.skeleton.append(("gender", ""))
        data.gender = line[1:]
        return

    if line[0] == "##case":
        if not projtype.allow_case:
            data.add_error(ERROR, lnum, "##case is not allowed in the project")
            return
        if len(line) == 1:
            data.add_error(ERROR, lnum, "##case takes a non-empty list of case names")
            return
        data.skeleton.append(("case", ""))
        data.case = [""] + line[1:]
        return

    data.skeleton.append(("pragma", line[0]))
    data.custom_pragmas[line[0]] = " ".join(line)
    return


string_pat = re.compile("^([A-Za-z_0-9]+)(\\.[A-Za-z0-9]+)?[ \\t]*:(.*)$")
bom = codecs.BOM_UTF8.decode("utf-8")


def load_language_file(projtype, text, lng_data=None):
    """
    Load a language file.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param text: Language file content.
    @type  text: C{str}

    @param lng_data: Suggested language, if specified.
    @type  lng_data: L{LanguageData} or C{None}

    @return: Loaded language data.
    @rtype:  L{NewGrfData}
    """
    data = NewGrfData()
    seen_strings = False
    skeleton_strings = set()

    if not projtype.has_grflangid and lng_data is not None:
        # If the project has no ##grflangid support, and there is lng_data provided, use it.
        data.set_lang(lng_data)

    for lnum, line in enumerate(text.split("\n")):
        line = line.rstrip()
        if line.startswith(bom):
            line = line[len(bom) :]

        # Comments either have 1 or >= 3 leading '#'.
        # The pragma ##id is special. It belongs to the skeleton, not to the header. Threat it like a comment.
        if line.startswith("##") and not line.startswith("###") and not line.startswith("##id"):
            if seen_strings:
                data.add_error(ERROR, lnum, "Cannot change language properties after processing strings")
                continue
            handle_pragma(projtype, lnum, line, data)
            continue

        if line == "" or line.startswith(";") or line.startswith("#"):
            data.skeleton.append(("literal", line))
            continue

        if not seen_strings:
            # Add obligatory but missing pragmas to the skeleton
            keys = set(s[0] for s in data.skeleton)

            # Stuff to put in front
            missing = []
            if projtype.has_grflangid and "grflangid" not in keys:
                missing.append(("grflangid", ""))
            data.skeleton[:0] = missing

            # Stuff to put at the end
            missing = []
            if "plural" not in keys:
                missing.append(("plural", ""))
            if projtype.allow_gender and "gender" not in keys:
                missing.append(("gender", ""))
            if projtype.allow_case and "case" not in keys:
                missing.append(("case", ""))

            pos = len(data.skeleton)
            while pos > 0 and data.skeleton[pos - 1][0] == "literal":
                pos -= 1
            data.skeleton[pos:pos] = missing

        m = string_pat.match(line)  # Regular string line?
        if m:
            seen_strings = True  # Disable processing of ## pragma lines
            if m.group(2) is None:
                m2 = ""
            else:
                m2 = m.group(2)[1:]
                if not projtype.allow_case and m2 != "":
                    # Silently discard ".case" string variants if the project doesn't allow them.
                    continue
            sv = StringValue(lnum, m.group(1), m2, m.group(3))
            data.strings.append(sv)
            if m2 == "":
                if m.group(1) in skeleton_strings:
                    data.add_error(ERROR, lnum, "String name {} is already used.".format(m.group(1)))
                    continue
                skeleton_strings.add(m.group(1))
                if "\t" in line:
                    normalized_line = line.expandtabs()
                else:
                    normalized_line = line
                data.skeleton.append(("string", (normalized_line.find(":"), m.group(1))))
            continue

        data.add_error(ERROR, lnum, "Line not recognized")

    for sv in data.strings:
        if sv.name not in skeleton_strings:
            data.add_error(
                ERROR, None, 'String name "{}" has no default definition (that is, without case).'.format(sv.name)
            )

    if data.language_data is None:
        data.add_error(ERROR, None, "Language file has no language identification (missing ##grflangid?)")

    data.cleanup_skeleton()
    return data


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
    txt = txt.replace("\n", "")
    txt = txt.replace("\r", "")

    # Strip white space in front of {}
    txt = re.sub(" +{}", "{}", txt)
    return txt


# Get string information
def compare_info(projtype, base_info, lng_info):
    """
    Compare both string uses with each other.
    Errors found during the comparison are added to the translation L{lng_info}.

    @param projtype: Project type.
    @type  projtype: L{ProjectType}

    @param base_info: Information about string parameters from the base language.
    @type  base_info: L{StringInfo}

    @param lng_info: Information about string parameters from the translation.
    @type  lng_info: L{StringInfo}

    @return: Whether both parameter uses are compatible.
    @rtype:  C{bool}
    """
    if base_info.has_error:
        return True  # Cannot blame the translation when the base language is broken.
    if lng_info.has_error:
        return False  # Translation has more serious problems.

    if len(base_info.commands) > len(lng_info.commands):
        msg = "String command for position {} (and further) is missing in the translation"
        msg = msg.format(len(lng_info.commands))
        lng_info.add_error(ERROR, None, msg)
        return False
    if len(base_info.commands) < len(lng_info.commands):
        msg = "String command for position {} (and further) is not used in the base language"
        msg = msg.format(len(base_info.commands))
        lng_info.add_error(ERROR, None, msg)
        return False

    for i, (base_name, lng_name) in enumerate(zip(base_info.commands, lng_info.commands)):
        if base_name is not None:
            base_name = base_name.get_translated_cmd()

        if lng_name is not None:
            lng_name = lng_name.literal

        if base_name != lng_name:
            if base_name is None:
                msg = "String command for position {} does not exist, the translation uses {}"
                msg = msg.format(i, "{" + lng_name + "}")
            elif lng_name is None:
                msg = "String command for position {} ({}) is missing in translation"
                msg = msg.format(i, "{" + base_name + "}")
            else:
                msg = "String command for position {} is wrong, base language uses {}, the translation uses {}"
                msg = msg.format(i, "{" + base_name + "}", "{" + lng_name + "}")
            lng_info.add_error(ERROR, None, msg)
            return False

    # Validate plural and gender references
    if not lng_info.check_plural_and_gender(base_info):
        return False

    # Non-positional commands must match in count.
    if base_info.non_positionals != lng_info.non_positionals:
        for bname, bcnt in base_info.non_positionals.items():
            if bname not in lng_info.non_positionals:
                msg = "String command {} is missing in the translation".format("{" + bname + "}")
                if is_critical_non_positional(projtype, bname):
                    lng_info.add_error(ERROR, None, msg)
                    return False
                else:
                    lng_info.add_error(WARNING, None, msg)
            elif lng_info.non_positionals[bname] != bcnt:
                # Non-positional is used both in base language and in translation, but a different number of times.
                # Requiring an exact match would give too much trouble, especially with ltr <-> rtl translations.
                msg = "String command {} is used {} times in the base language, and {} times in the translation"
                msg = msg.format("{" + bname + "}", bcnt, lng_info.non_positionals[bname])
                lng_info.add_error(WARNING, None, msg)

        for np in lng_info.non_positionals:
            if np not in base_info.non_positionals:
                msg = "String command {} is not used in the base language".format("{" + np + "}")
                if is_critical_non_positional(projtype, np):
                    lng_info.add_error(ERROR, None, msg)
                    return False
                else:
                    lng_info.add_error(WARNING, None, msg)

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
    if name == "":
        sc = NL_PARAMETER
    elif name == "{":
        sc = CURLY_PARAMETER
    else:
        sc = projtype.text_commands.get(name)
        if sc is None:
            return True

    return sc.critical
