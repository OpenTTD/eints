"""
The type of project decides what language string primitives exist, and how they should be used.
"""

from webtranslate.parameter_info_table import (
    NEWGRF_PARAMETERS,
    GS_PARAMETERS,
    OPENTTD_PARAMETERS,
)


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

    @ivar allow_unstable_lng: Allow translation of 'unstable' languages.
    @type allow_unstable_lng: C{bool}

    @ivar has_grflangid: Project uses '##grflangid' in the language file for identifying the language.
    @type has_grflangid: C{bool}

    @ivar base_is_translated_cache: Whether string commands in the base language may be rewritten before display.
    @type base_is_translated_cache: C{None} means 'unknown', otherwise C{bool}.
    """

    def __init__(
        self, name, human_name, text_commands, allow_gender, allow_case, allow_extra, allow_unstable_lng, has_grflangid
    ):
        self.name = name
        self.human_name = human_name
        self.text_commands = text_commands
        self.allow_gender = allow_gender
        self.allow_case = allow_case
        self.allow_extra = allow_extra
        self.allow_unstable_lng = allow_unstable_lng
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

    def allow_language(self, linfo):
        """
        Is the provided language allowed to be used by the projects of this type?

        @param linfo: Language meta-data.
        @type  linfo: L{LanguageData}

        @return: Whether the language may be used by project of the project type.
        @rtype:  C{bool}
        """
        return linfo.is_stable or self.allow_unstable_lng


class NewGRFProject(ProjectType):
    """
    Project type for NewGRF strings.
    """

    def __init__(self):
        ProjectType.__init__(
            self,
            name="newgrf",
            human_name="NewGrf",
            text_commands=NEWGRF_PARAMETERS,
            allow_gender=True,
            allow_case=True,
            allow_extra=True,
            allow_unstable_lng=False,
            has_grflangid=True,
        )


class GameScriptProject(ProjectType):
    """
    Project type for game script strings.
    """

    def __init__(self):
        ProjectType.__init__(
            self,
            name="game-script",
            human_name="GameScript",
            text_commands=GS_PARAMETERS,
            allow_gender=False,
            allow_case=False,
            allow_extra=False,
            allow_unstable_lng=False,
            has_grflangid=False,
        )


class OpenTTDProject(ProjectType):
    """
    Project type for OpenTTD strings.
    """

    def __init__(self):
        ProjectType.__init__(
            self,
            name="openttd",
            human_name="OpenTTD",
            text_commands=OPENTTD_PARAMETERS,
            allow_gender=True,
            allow_case=True,
            allow_extra=False,
            allow_unstable_lng=True,
            has_grflangid=True,
        )


# Available project types, ordered by internal name.
project_types = {}
for pt in [NewGRFProject(), GameScriptProject(), OpenTTDProject()]:
    project_types[pt.name] = pt
