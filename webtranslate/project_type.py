"""
The type of project decides what language string primitives exist, and how they should be used.
"""

class ProjectType:
    """
    Base class of the project type.

    @ivar name: Name of the project type.
    @type name: C{str}

    @ivar human_name: Human readable name of the project type.
    @type human_name: C{str}

    @ivar text_commands: All regular commands, ordered by name.
    @type text_commands: C{dict} of C{str} to L{ParameterInfo}

    @ivar allow_gender: Allow gender string commands.
    @type allow_gender: C{bool}

    @ivar allow_case: Allow string cases.
    @type allow_case: C{bool}

    @ivar allow_extra: Allow extra string commands (that is, custom tags).
    @type allow_extra: C{bool}

    @ivar has_grflangid: Project uses '##grflangid' in the language file for identifying the language.
    @type has_grflangid: C{bool}

    @ivar base_is_translated_cache: Whether string commands in the base language may be rewritten before display.
    @type base_is_translated_cache: C{None} means 'unknown', otherwise C{bool}.
    """
    def __init__(self, name, human_name, text_commands, allow_gender, allow_case, allow_extra, has_grflangid):
        self.name = name
        self.human_name = human_name
        self.text_commands = text_commands
        self.allow_gender = allow_gender
        self.allow_case = allow_case
        self.allow_extra = allow_extra
        self.has_grflangid = has_grflangid
        self.base_is_translated_cache = None

    def is_base_translated(self):
        """
        Return whether strings in the base language may have been modified to
        match better with the required translation, when they are displayed at
        the string edit form.

        An example of the above is the {RAW_STRING} -> {STRING} mapping.

        @return: Whether strings in the base language may be changed before displaying them for translating.
        @rtype:  C{bool}
        """
        if self.base_is_translated_cache is None:
            self.base_is_translated_cache = False
            for pi in self.text_commands.values():
                if pi.translated_cmd is not None:
                    self.base_is_translated_cache = True
                    break
        return self.base_is_translated_cache


class NewGRFProject(ProjectType):
    """
    Project type for NewGRF strings.
    """
    def __init__(self):
        ProjectType.__init__(self,
            name = "newgrf",
            human_name = "NewGrf",
            text_commands = NEWGRF_PARAMETERS,
            allow_gender = True,
            allow_case = True,
            allow_extra = True,
            has_grflangid = True)

class GameScriptProject(ProjectType):
    """
    Project type for game script strings.
    """
    def __init__(self):
        ProjectType.__init__(self,
            name = "game-script",
            human_name = "GameScript",
            text_commands = GS_PARAMETERS,
            allow_gender = False,
            allow_case = False,
            allow_extra = False,
            has_grflangid = False)

class OpenTTDProject(ProjectType):
    """
    Project type for OpenTTD strings.
    """
    def __init__(self):
        ProjectType.__init__(self,
            name = "openttd",
            human_name = "OpenTTD",
            text_commands = OPENTTD_PARAMETERS,
            allow_gender = True,
            allow_case = True,
            allow_extra = False,
            has_grflangid = True)

class ParameterInfo:
    """
    @ivar literal: Text of the literal (without curly brackets).
    @type literal: C{str}

    @ivar parameters: For each parameter whether it is suitable for plural or gender forms.
    @type parameters: C{list} of (C{bool}, C{bool})

    @ivar default_plural_pos: Default parameter subposition for plural forms.
    @type default_plural_pos: C{int} or C{None}

    @ivar allow_case: May have a ".case" suffix.
    @type allow_case: C{bool}

    @ivar critical: String command is critical, its count should match between the base language and the translation.
    @type critical: C{bool}

    @ivar translated_cmd: For commands in the base language, command to use checking and displaying.
    @type translated_cmd: C{str} or C{None} (the latter means use C{self})
    """
    def __init__(self, literal, parameters, default_plural_pos, allow_case, critical, translated_cmd = None):
        self.literal = literal
        self.parameters = parameters
        self.default_plural_pos = default_plural_pos
        self.allow_case = allow_case
        self.critical = critical
        self.translated_cmd = translated_cmd
        assert default_plural_pos is None or parameters[default_plural_pos][0]

    def use_plural(self, subindex):
        """
        Check whether a parameter can be used for plural forms.

        @param subindex: Parameter index.
        @type  subindex: C{int}

        @return: True if suitable for plural form.
        @rtype:  C{bool}
        """
        return subindex >= 0 and subindex < len(self.parameters) and self.parameters[subindex][0]

    def use_gender(self, subindex):
        """
        Check whether a parameter can be used for gender forms.

        @param subindex: Parameter index.
        @type  subindex: C{int}

        @return: True if suitable for gender form.
        @rtype:  C{bool}
        """
        return subindex >= 0 and subindex < len(self.parameters) and self.parameters[subindex][1]

    def get_translated_cmd(self):
        """
        Get the command name to use for a translation.

        @return: The command name to use for a translation.
        @rtype:  C{str}
        """
        if self.translated_cmd is None: return self.literal
        return self.translated_cmd

P__ = (False, False) # Parameter, not suitable for plural or gender
PP_ = (True,  False) # Parameter suitable for plural
P_G = (False, True)  # Parameter suitable for gender
PPG = (True,  True)  # Parameter suitable for both plural and gender

# {{{ NEWGRF_PARAMETERS
_NEWGRF_PARAMETERS = [
    ParameterInfo("NBSP",           [], None, False, False),
    ParameterInfo("COPYRIGHT",      [], None, False, True ),
    ParameterInfo("TRAIN",          [], None, False, True ),
    ParameterInfo("LORRY",          [], None, False, True ),
    ParameterInfo("BUS",            [], None, False, True ),
    ParameterInfo("PLANE",          [], None, False, True ),
    ParameterInfo("SHIP",           [], None, False, True ),
    ParameterInfo("TINYFONT",       [], None, False, True ),
    ParameterInfo("BIGFONT",        [], None, False, True ),
    ParameterInfo("BLUE",           [], None, False, True ),
    ParameterInfo("SILVER",         [], None, False, True ),
    ParameterInfo("GOLD",           [], None, False, True ),
    ParameterInfo("RED",            [], None, False, True ),
    ParameterInfo("PURPLE",         [], None, False, True ),
    ParameterInfo("LTBROWN",        [], None, False, True ),
    ParameterInfo("ORANGE",         [], None, False, True ),
    ParameterInfo("GREEN",          [], None, False, True ),
    ParameterInfo("YELLOW",         [], None, False, True ),
    ParameterInfo("DKGREEN",        [], None, False, True ),
    ParameterInfo("CREAM",          [], None, False, True ),
    ParameterInfo("BROWN",          [], None, False, True ),
    ParameterInfo("WHITE",          [], None, False, True ),
    ParameterInfo("LTBLUE",         [], None, False, True ),
    ParameterInfo("GRAY",           [], None, False, True ),
    ParameterInfo("DKBLUE",         [], None, False, True ),
    ParameterInfo("BLACK",          [], None, False, True ),

    ParameterInfo("COMMA",          [PP_],      0,    False, True ),
    ParameterInfo("SIGNED_WORD",    [PP_],      0,    False, True ),
    ParameterInfo("UNSIGNED_WORD",  [PP_],      0,    False, True ),
    ParameterInfo("CURRENCY",       [PP_],      0,    False, True ),
    ParameterInfo("VELOCITY",       [PP_],      0,    False, True ),
    ParameterInfo("VOLUME",         [PP_],      0,    False, True ),
    ParameterInfo("VOLUME_SHORT",   [PP_],      0,    False, True ),
    ParameterInfo("POWER",          [PP_],      0,    False, True ),
    ParameterInfo("WEIGHT",         [PP_],      0,    False, True ),
    ParameterInfo("WEIGHT_SHORT",   [PP_],      0,    False, True ),
    ParameterInfo("CARGO_LONG",     [P_G, PP_], 1,    False, True ),
    ParameterInfo("CARGO_SHORT",    [P__, PP_], 1,    False, True ), # short cargo description, only ### tons, or ### litres
    ParameterInfo("CARGO_TINY",     [P__, PP_], 1,    False, True ), # tiny cargo description with only the amount
    ParameterInfo("HEX",            [PP_],      0,    False, True ),
    ParameterInfo("STRING",         [P_G],      None, True,  True ),
    ParameterInfo("DATE1920_LONG",  [P__],      None, False, True ),
    ParameterInfo("DATE1920_SHORT", [P__],      None, False, True ),
    ParameterInfo("DATE_LONG",      [P__],      None, False, True ),
    ParameterInfo("DATE_SHORT",     [P__],      None, False, True ),
    ParameterInfo("POP_WORD",       [P__],      None, False, True ),
    ParameterInfo("STATION",        [P__],      None, False, True ),
]

NEWGRF_PARAMETERS = dict((x.literal, x) for x in _NEWGRF_PARAMETERS)
# }}}
# {{{ GS_PARAMETERS
# Based on OpenTTD src/tables/strgen_tables.h r26050
_GS_PARAMETERS = [
    ParameterInfo("TINY_FONT",         [], None, False, True ),
    ParameterInfo("BIG_FONT",          [], None, False, True ),

    ParameterInfo("BLUE",              [], None, False, False),
    ParameterInfo("SILVER",            [], None, False, False),
    ParameterInfo("GOLD",              [], None, False, False),
    ParameterInfo("RED",               [], None, False, False),
    ParameterInfo("PURPLE",            [], None, False, False),
    ParameterInfo("LTBROWN",           [], None, False, False),
    ParameterInfo("ORANGE",            [], None, False, False),
    ParameterInfo("GREEN",             [], None, False, False),
    ParameterInfo("YELLOW",            [], None, False, False),
    ParameterInfo("DKGREEN",           [], None, False, False),
    ParameterInfo("CREAM",             [], None, False, False),
    ParameterInfo("BROWN",             [], None, False, False),
    ParameterInfo("WHITE",             [], None, False, False),
    ParameterInfo("LTBLUE",            [], None, False, False),
    ParameterInfo("GRAY",              [], None, False, False),
    ParameterInfo("DKBLUE",            [], None, False, False),
    ParameterInfo("BLACK",             [], None, False, False),

    ParameterInfo("STRING1",           [P_G, PPG],                               None, True,  True,  "STRING"),
    ParameterInfo("STRING2",           [P_G, PPG, PPG],                          None, True,  True,  "STRING"),
    ParameterInfo("STRING3",           [P_G, PPG, PPG, PPG],                     None, True,  True,  "STRING"),
    ParameterInfo("STRING4",           [P_G, PPG, PPG, PPG, PPG],                None, True,  True,  "STRING"),
    ParameterInfo("STRING5",           [P_G, PPG, PPG, PPG, PPG, PPG],           None, True,  True,  "STRING"),
    ParameterInfo("STRING6",           [P_G, PPG, PPG, PPG, PPG, PPG, PPG],      None, True,  True,  "STRING"),
    ParameterInfo("STRING7",           [P_G, PPG, PPG, PPG, PPG, PPG, PPG, PPG], None, True,  True,  "STRING"),

    ParameterInfo("INDUSTRY",          [P_G],      None, True,  True ), # takes an industry number.
    ParameterInfo("CARGO_LONG",        [P_G, PP_], 1,    False, True ),
    ParameterInfo("CARGO_SHORT",       [P__, PP_], 1,    False, True ), # short cargo description, only ### tons, or ### litres
    ParameterInfo("CARGO_TINY",        [P__, PP_], 1,    False, True ), # tiny cargo description with only the amount
    ParameterInfo("CARGO_LIST",        [P__],      None, True,  True ),
    ParameterInfo("POWER",             [PP_],      0,    False, True ),
    ParameterInfo("VOLUME_LONG",       [PP_],      0,    False, True ),
    ParameterInfo("VOLUME_SHORT",      [PP_],      0,    False, True ),
    ParameterInfo("WEIGHT_LONG",       [PP_],      0,    False, True ),
    ParameterInfo("WEIGHT_SHORT",      [PP_],      0,    False, True ),
    ParameterInfo("FORCE",             [PP_],      0,    False, True ),
    ParameterInfo("VELOCITY",          [PP_],      0,    False, True ),
    ParameterInfo("HEIGHT",            [PP_],      0,    False, True ),
    ParameterInfo("DATE_TINY",         [P__],      None, False, True ),
    ParameterInfo("DATE_SHORT",        [P__],      None, True,  True ),
    ParameterInfo("DATE_LONG",         [P__],      None, True,  True ),
    ParameterInfo("DATE_ISO",          [P__],      None, False, True ),

    ParameterInfo("STRING",            [P_G],      None, True,  True ),
    ParameterInfo("RAW_STRING",        [P_G],      None, False, True,  "STRING"),

    ParameterInfo("COMMA",             [PP_],      0,    False, True ), # Number with comma
    ParameterInfo("DECIMAL",           [PP_, P__], 0,    False, True ), # Number with comma and fractional part.
    ParameterInfo("NUM",               [PP_],      0,    False, True ), # Signed number
    ParameterInfo("ZEROFILL_NUM",      [PP_, P__], 0,    False, True ), # Unsigned number with zero fill, e.g. "02".
    ParameterInfo("BYTES",             [PP_],      0,    False, True ), # Unsigned number with "bytes", i.e. "1.02 MiB or 123 KiB"
    ParameterInfo("HEX",               [PP_],      0,    False, True ), # Hexadecimally printed number

    ParameterInfo("CURRENCY_LONG",     [PP_],      0,    False, True ),
    ParameterInfo("CURRENCY_SHORT",    [PP_],      0,    False, True ), # compact currency

    ParameterInfo("WAYPOINT",          [P_G],      None, False, True ), # waypoint name
    ParameterInfo("STATION",           [P_G],      None, False, True ),
    ParameterInfo("DEPOT",             [P_G, P__], None, False, True ),
    ParameterInfo("TOWN",              [P_G],      None, False, True ),
    ParameterInfo("GROUP",             [P_G],      None, False, True ),
    ParameterInfo("SIGN",              [P_G],      None, False, True ),
    ParameterInfo("ENGINE",            [P_G],      None, False, True ),
    ParameterInfo("VEHICLE",           [P_G],      None, False, True ),
    ParameterInfo("COMPANY",           [P_G],      None, False, True ),
    ParameterInfo("COMPANY_NUM",       [P__],      None, False, True ),
    ParameterInfo("PRESIDENT_NAME",    [P_G],      None, False, True ),

    ParameterInfo("TRAIN",             [], None, False, True ),
    ParameterInfo("LORRY",             [], None, False, True ),
    ParameterInfo("BUS",               [], None, False, True ),
    ParameterInfo("PLANE",             [], None, False, True ),
    ParameterInfo("SHIP",              [], None, False, True ),
    ParameterInfo("NBSP",              [], None, False, False),
    ParameterInfo("COPYRIGHT",         [], None, False, True ),

    # The following are directional formatting codes used to get the RTL strings right:
    # http://www.unicode.org/unicode/reports/tr9/#Directional_Formatting_Codes
    ParameterInfo("LRM",               [], None, False, False),
    ParameterInfo("RLM",               [], None, False, False),
    ParameterInfo("LRE",               [], None, False, False),
    ParameterInfo("RLE",               [], None, False, False),
    ParameterInfo("LRO",               [], None, False, False),
    ParameterInfo("RLO",               [], None, False, False),
    ParameterInfo("PDF",               [], None, False, False),
]

GS_PARAMETERS = dict((x.literal, x) for x in _GS_PARAMETERS)
# }}}
# {{{ OPENTTD_PARAMETERS
# Based on OpenTTD src/tables/strgen_tables.h r26050
_OPENTTD_PARAMETERS = [
    # Some string parameters are only allowed in the OpenTTD project.
    # While they technically also work in Game Scripts, disencourage the usage.
    # This also includes the "sprite" characters.
    ParameterInfo("REV",               [],    None, False, True ),
    ParameterInfo("STATION_FEATURES",  [P__], None, False, True ), # station features string, icons of the features
    ParameterInfo("UP_ARROW",          [],    None, False, True ),
    ParameterInfo("SMALL_UP_ARROW",    [],    None, False, True ),
    ParameterInfo("SMALL_DOWN_ARROW",  [],    None, False, True ),
    ParameterInfo("DOWN_ARROW",        [],    None, False, True ),
    ParameterInfo("CHECKMARK",         [],    None, False, True ),
    ParameterInfo("CROSS",             [],    None, False, True ),
    ParameterInfo("RIGHT_ARROW",       [],    None, False, False), # left/right arrows are not critical due to LTR/RTL languages
    ParameterInfo("SMALL_LEFT_ARROW",  [],    None, False, False),
    ParameterInfo("SMALL_RIGHT_ARROW", [],    None, False, False),
]

OPENTTD_PARAMETERS = dict((x.literal, x) for x in _OPENTTD_PARAMETERS)
OPENTTD_PARAMETERS.update((x.literal, x) for x in _GS_PARAMETERS)
# }}}

NL_PARAMETER    = ParameterInfo("",  [], None, False, False)
CURLY_PARAMETER = ParameterInfo("{", [], None, False, False)


# Available project types, ordered by internal name.
project_types = {}
for pt in [NewGRFProject(), GameScriptProject(), OpenTTDProject()]:
    project_types[pt.name] = pt

