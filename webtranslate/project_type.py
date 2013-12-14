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

    @ivar allow_gender: Allow string cases.
    @type allow_gender: C{bool}

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

class ParameterInfo:
    """
    @ivar literal: Text of the literal (without curly brackets).
    @type literal: C{str}

    @ivar takes_param: Takes a string parameter.
    @type takes_param: C{bool}

    @ivar use_plural: May be used for plural.
    @type use_plural: C{bool}

    @ivar use_gender: May be used for gender.
    @type use_gender: C{bool}

    @ivar allow_case: May have a ".case" suffix.
    @type allow_case: C{bool}

    @ivar critical: String command is critical, its count should match between the base language and the translation.
    @type critical: C{bool}

    @ivar translated_cmd: For commands in the base language, command to use checking and displaying.
    @type translated_cmd: C{str} or C{None} (the latter means use C{self})
    """
    def __init__(self, literal, takes_param, use_plural, use_gender, allow_case, critical, translated_cmd = None):
        self.literal = literal
        self.takes_param = takes_param
        self.use_plural = use_plural
        self.use_gender = use_gender
        self.allow_case = allow_case
        self.critical = critical
        self.translated_cmd = translated_cmd

    def get_translated_cmd(self):
        """
        Get the command name to use for a translation.

        @return: The command name to use for a translation.
        @rtype:  C{str}
        """
        if self.translated_cmd is None: return self.literal
        return self.translated_cmd

# {{{ NEWGRF_PARAMETERS
_NEWGRF_PARAMETERS = [
    ParameterInfo("NBSP",           False, False, False, False, False),
    ParameterInfo("COPYRIGHT",      False, False, False, False, True ),
    ParameterInfo("TRAIN",          False, False, False, False, True ),
    ParameterInfo("LORRY",          False, False, False, False, True ),
    ParameterInfo("BUS",            False, False, False, False, True ),
    ParameterInfo("PLANE",          False, False, False, False, True ),
    ParameterInfo("SHIP",           False, False, False, False, True ),
    ParameterInfo("TINYFONT",       False, False, False, False, True ),
    ParameterInfo("BIGFONT",        False, False, False, False, True ),
    ParameterInfo("BLUE",           False, False, False, False, True ),
    ParameterInfo("SILVER",         False, False, False, False, True ),
    ParameterInfo("GOLD",           False, False, False, False, True ),
    ParameterInfo("RED",            False, False, False, False, True ),
    ParameterInfo("PURPLE",         False, False, False, False, True ),
    ParameterInfo("LTBROWN",        False, False, False, False, True ),
    ParameterInfo("ORANGE",         False, False, False, False, True ),
    ParameterInfo("GREEN",          False, False, False, False, True ),
    ParameterInfo("YELLOW",         False, False, False, False, True ),
    ParameterInfo("DKGREEN",        False, False, False, False, True ),
    ParameterInfo("CREAM",          False, False, False, False, True ),
    ParameterInfo("BROWN",          False, False, False, False, True ),
    ParameterInfo("WHITE",          False, False, False, False, True ),
    ParameterInfo("LTBLUE",         False, False, False, False, True ),
    ParameterInfo("GRAY",           False, False, False, False, True ),
    ParameterInfo("DKBLUE",         False, False, False, False, True ),
    ParameterInfo("BLACK",          False, False, False, False, True ),

    ParameterInfo("COMMA",          True,  True,  False, False, True ),
    ParameterInfo("SIGNED_WORD",    True,  True,  False, False, True ),
    ParameterInfo("UNSIGNED_WORD",  True,  True,  False, False, True ),
    ParameterInfo("CURRENCY",       True,  False, False, False, True ),
    ParameterInfo("VELOCITY",       True,  False, False, False, True ),
    ParameterInfo("VOLUME",         True,  False, False, False, True ),
    ParameterInfo("VOLUME_SHORT",   True,  False, False, False, True ),
    ParameterInfo("POWER",          True,  False, False, False, True ),
    ParameterInfo("WEIGHT",         True,  False, False, False, True ),
    ParameterInfo("WEIGHT_SHORT",   True,  False, False, False, True ),
    ParameterInfo("HEX",            True,  True,  False, False, True ),
    ParameterInfo("STRING",         True,  False, True , True,  True ),
    ParameterInfo("DATE1920_LONG",  True,  False, False, False, True ),
    ParameterInfo("DATE1920_SHORT", True,  False, False, False, True ),
    ParameterInfo("DATE_LONG",      True,  False, False, False, True ),
    ParameterInfo("DATE_SHORT",     True,  False, False, False, True ),
    ParameterInfo("POP_WORD",       True,  False, False, False, True ),
    ParameterInfo("STATION",        True,  False, False, False, True ),
]

NEWGRF_PARAMETERS = dict((x.literal, x) for x in _NEWGRF_PARAMETERS)
# }}}
# {{{ GS_PARAMETERS
# Based on OpenTTD src/tables/strgen_tables.h r26050
_GS_PARAMETERS = [
    ParameterInfo("TINY_FONT",         False, False, False, False, True ),
    ParameterInfo("BIG_FONT",          False, False, False, False, True ),

    ParameterInfo("BLUE",              False, False, False, False, False),
    ParameterInfo("SILVER",            False, False, False, False, False),
    ParameterInfo("GOLD",              False, False, False, False, False),
    ParameterInfo("RED",               False, False, False, False, False),
    ParameterInfo("PURPLE",            False, False, False, False, False),
    ParameterInfo("LTBROWN",           False, False, False, False, False),
    ParameterInfo("ORANGE",            False, False, False, False, False),
    ParameterInfo("GREEN",             False, False, False, False, False),
    ParameterInfo("YELLOW",            False, False, False, False, False),
    ParameterInfo("DKGREEN",           False, False, False, False, False),
    ParameterInfo("CREAM",             False, False, False, False, False),
    ParameterInfo("BROWN",             False, False, False, False, False),
    ParameterInfo("WHITE",             False, False, False, False, False),
    ParameterInfo("LTBLUE",            False, False, False, False, False),
    ParameterInfo("GRAY",              False, False, False, False, False),
    ParameterInfo("DKBLUE",            False, False, False, False, False),
    ParameterInfo("BLACK",             False, False, False, False, False),
#    ParameterInfo("REV",               False, False, False, False, True ),

    ParameterInfo("STRING1",           True,  True,  True,  True,  True,  "STRING"),
    ParameterInfo("STRING2",           True,  True,  True,  True,  True,  "STRING"),
    ParameterInfo("STRING3",           True,  True,  True,  True,  True,  "STRING"),
    ParameterInfo("STRING4",           True,  True,  True,  True,  True,  "STRING"),
    ParameterInfo("STRING5",           True,  True,  True,  True,  True,  "STRING"),
    ParameterInfo("STRING6",           True,  True,  True,  True,  True,  "STRING"),
    ParameterInfo("STRING7",           True,  True,  True,  True,  True,  "STRING"),

#    ParameterInfo("STATION_FEATURES",  True,  False, False, False, True ), # station features string, icons of the features
    ParameterInfo("INDUSTRY",          True,  False, True,  True,  True ), # takes an industry number.
    ParameterInfo("CARGO_LONG",        True,  False, True,  False, True ),
    ParameterInfo("CARGO_SHORT",       True,  False, False, False, True ), # short cargo description, only ### tons, or ### litres
    ParameterInfo("CARGO_TINY",        True,  False, False, False, True ), # tiny cargo description with only the amount
    ParameterInfo("CARGO_LIST",        True,  False, False, True,  True ),
    ParameterInfo("POWER",             True,  False, False, False, True ),
    ParameterInfo("VOLUME_LONG",       True,  False, False, False, True ),
    ParameterInfo("VOLUME_SHORT",      True,  False, False, False, True ),
    ParameterInfo("WEIGHT_LONG",       True,  False, False, False, True ),
    ParameterInfo("WEIGHT_SHORT",      True,  False, False, False, True ),
    ParameterInfo("FORCE",             True,  False, False, False, True ),
    ParameterInfo("VELOCITY",          True,  False, False, False, True ),
    ParameterInfo("HEIGHT",            True,  False, False, False, True ),
    ParameterInfo("DATE_TINY",         True,  False, False, False, True ),
    ParameterInfo("DATE_SHORT",        True,  False, False, True,  True ),
    ParameterInfo("DATE_LONG",         True,  False, False, True,  True ),
    ParameterInfo("DATE_ISO",          True,  False, False, False, True ),

    ParameterInfo("STRING",            True,  True,  True,  True,  True ),
    ParameterInfo("RAW_STRING",        True,  True,  True,  False, True,  "STRING"),

    ParameterInfo("COMMA",             True,  True,  False, False, True ), # Number with comma
    ParameterInfo("DECIMAL",           True,  True,  False, False, True ), # Number with comma and fractional part.
    ParameterInfo("NUM",               True,  True,  False, False, True ), # Signed number
    ParameterInfo("ZEROFILL_NUM",      True,  True,  False, False, True ), # Unsigned number with zero fill, e.g. "02".
    ParameterInfo("BYTES",             True,  True,  False, False, True ), # Unsigned number with "bytes", i.e. "1.02 MiB or 123 KiB"
    ParameterInfo("HEX",               True,  True,  False, False, True ), # Hexadecimally printed number

    ParameterInfo("CURRENCY_LONG",     True,  True,  False, False, True ),
    ParameterInfo("CURRENCY_SHORT",    True,  True,  False, False, True ), # compact currency

    ParameterInfo("WAYPOINT",          True,  False, True,  False, True ), # waypoint name
    ParameterInfo("STATION",           True,  False, True,  False, True ),
    ParameterInfo("DEPOT",             True,  False, True,  False, True ),
    ParameterInfo("TOWN",              True,  False, True,  False, True ),
    ParameterInfo("GROUP",             True,  False, True,  False, True ),
    ParameterInfo("SIGN",              True,  False, True,  False, True ),
    ParameterInfo("ENGINE",            True,  False, True,  False, True ),
    ParameterInfo("VEHICLE",           True,  False, True,  False, True ),
    ParameterInfo("COMPANY",           True,  False, True,  False, True ),
    ParameterInfo("COMPANY_NUM",       True,  False, False, False, True ),
    ParameterInfo("PRESIDENT_NAME",    True,  False, True,  False, True ),

#    ParameterInfo("UP_ARROW",          False, False, False, False, True ),
#    ParameterInfo("SMALL_UP_ARROW",    False, False, False, False, True ),
#    ParameterInfo("SMALL_DOWN_ARROW",  False, False, False, False, True ),
    ParameterInfo("TRAIN",             False, False, False, False, True ),
    ParameterInfo("LORRY",             False, False, False, False, True ),
    ParameterInfo("BUS",               False, False, False, False, True ),
    ParameterInfo("PLANE",             False, False, False, False, True ),
    ParameterInfo("SHIP",              False, False, False, False, True ),
    ParameterInfo("NBSP",              False, False, False, False, False),
    ParameterInfo("COPYRIGHT",         False, False, False, False, True ),
#    ParameterInfo("DOWN_ARROW",        False, False, False, False, True ),
#    ParameterInfo("CHECKMARK",         False, False, False, False, True ),
#    ParameterInfo("CROSS",             False, False, False, False, True ),
#    ParameterInfo("RIGHT_ARROW",       False, False, False, False, False),
#    ParameterInfo("SMALL_LEFT_ARROW",  False, False, False, False, False),
#    ParameterInfo("SMALL_RIGHT_ARROW", False, False, False, False, False),

    # The following are directional formatting codes used to get the RTL strings right:
    # http://www.unicode.org/unicode/reports/tr9/#Directional_Formatting_Codes
    ParameterInfo("LRM",               False, False, False, False, False),
    ParameterInfo("RLM",               False, False, False, False, False),
    ParameterInfo("LRE",               False, False, False, False, False),
    ParameterInfo("RLE",               False, False, False, False, False),
    ParameterInfo("LRO",               False, False, False, False, False),
    ParameterInfo("RLO",               False, False, False, False, False),
    ParameterInfo("PDF",               False, False, False, False, False),
]

GS_PARAMETERS = dict((x.literal, x) for x in _GS_PARAMETERS)
# }}}

NL_PARAMETER    = ParameterInfo("",  False, False, False, False, False)
CURLY_PARAMETER = ParameterInfo("{", False, False, False, False, True)


# Available project types, ordered by internal name.
project_types = {}
for pt in [NewGRFProject(), GameScriptProject()]:
    project_types[pt.name] = pt

