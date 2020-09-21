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

    def __init__(self, literal, parameters, default_plural_pos, allow_case, critical, translated_cmd=None):
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
        if self.translated_cmd is None:
            return self.literal
        return self.translated_cmd
