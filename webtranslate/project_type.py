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
    """
    def __init__(self, name, human_name, text_commands, allow_gender, allow_case):
        self.name = name
        self.human_name = human_name
        self.text_commands = text_commands
        self.allow_gender = allow_gender
        self.allow_case = allow_case

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
            allow_case = True)


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
    """
    def __init__(self, literal, takes_param, use_plural, use_gender, allow_case, critical):
        self.literal = literal
        self.takes_param = takes_param
        self.use_plural = use_plural
        self.use_gender = use_gender
        self.allow_case = allow_case
        self.critical = critical

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

NL_PARAMETER    = ParameterInfo("",  False, False, False, False, False)
CURLY_PARAMETER = ParameterInfo("{", False, False, False, False, True)


# Available project types, ordered by internal name.
project_types = {}
for pt in [NewGRFProject()]:
    project_types[pt.name] = pt

