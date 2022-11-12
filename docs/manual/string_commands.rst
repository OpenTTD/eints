
.. _string-commands-list:

===================
String command list
===================

Below is the full table of string commands. It has been split in four parts,
based on project type and command type.

- :ref:`nonpos-newgrf-string_commands`
- :ref:`pos-newgrf-string_commands`
- :ref:`nonpos-gamescript-string_commands`
- :ref:`pos-gamescript-string_commands`


.. _nonpos-newgrf-string_commands:

Non-positional NewGrf string commands
=====================================

================= ===========================================================
Command           Effect
================= ===========================================================
``{}``            Continue at the next line
``{{}``           Output a ``{``
``{NBSP}``        Display a non-breaking space
``{COPYRIGHT}``   Display a copyright symbol
``{TRAIN}``       Display a train symbol
``{LORRY}``       Display a truck symbol
``{BUS}``         Display a bus symbol
``{PLANE}``       Display a plane symbol
``{SHIP}``        Display a ship symbol
``{TINYFONT}``    Switch to a small font
``{BIGFONT}``     Switch to a big font
``{BLUE}``        Output following text in blue colour
``{SILVER}``      Output following text in silver colour
``{GOLD}``        Output following text in gold colour
``{RED}``         Output following text in red colour
``{PURPLE}``      Output following text in purple colour
``{LTBROWN}``     Output following text in light brown colour
``{ORANGE}``      Output following text in orange colour
``{GREEN}``       Output following text in green colour
``{YELLOW}``      Output following text in yellow colour
``{DKGREEN}``     Output following text in dark green colour
``{CREAM}``       Output following text in cream colour
``{BROWN}``       Output following text in brown colour
``{WHITE}``       Output following text in white colour
``{LTBLUE}``      Output following text in light blue colour
``{GRAY}``        Output following text in gray colour
``{DKBLUE}``      Output following text in dark blue colour
``{BLACK}``       Output following text in black colour
``{PUSH_COLOUR}`` Store the current colour
``{POP_COLOUR}``  Restore last saved colour
================= ===========================================================

.. _pos-newgrf-string_commands:

Positional NewGrf string commands
=================================

==================== ====== ====== =======================================
Command              Plural Gender Effect
==================== ====== ====== =======================================
``{COMMA}``           yes     no   Insert number into the text
``{SIGNED_WORD}``     yes     no   Insert number into the text
``{UNSIGNED_WORD}``   yes     no   Insert positive number into the text
``{HEX}``             yes     no   Insert hexadecimal number into the text
``{STRING}``           no    yes   Insert a string into the text
``{CURRENCY}``         no     no   Insert an amount into the text
``{VELOCITY}``         no     no   Insert a speed into the text
``{VOLUME}``           no     no   Insert a volume into the text
``{VOLUME_SHORT}``     no     no   Insert a volume into the text
``{POWER}``            no     no   Insert an horse-power into the text
``{WEIGHT}``           no     no   Insert a weight into the text
``{WEIGHT_SHORT}``     no     no   Insert a weight into the text
``{CARGO_LONG}``       no    yes   Insert a cargo amount into the text
``{CARGO_SHORT}``      no     no   Insert a cargo amount into the text
``{CARGO_TINY}``       no     no   Insert a cargo amount into the text
``{CARGO_NAME}``       no    yes   Insert a cargo name into the text
``{STATION}``          no     no   Insert a station name into the text
``{DATE1920_LONG}``    no     no   Insert a date into the text
``{DATE1920_SHORT}``   no     no   Insert a weight into the text
``{DATE_LONG}``        no     no   Insert a weight into the text
``{DATE_SHORT}``       no     no   Insert a weight into the text
``{POP_WORD}``         no     no   Insert nothing (and drop an argument)
==================== ====== ====== =======================================


.. _nonpos-gamescript-string_commands:

Non-positional GameScript string commands
=========================================

The list is the same as :ref:`nonpos-newgrf-string_commands`, except the
``{TINY_FONT}`` and ``{BIG_FONT}`` are written differently, and there are new
seven commands for handling right to left (RTL) languages.

======================= ============================================================================
Command                 Effect
======================= ============================================================================
``{}``                  Continue at the next line
``{{}``                 Output a ``{``
``{NBSP}``              Display a non-breaking space
``{COPYRIGHT}``         Display a copyright symbol
``{TRAIN}``             Output a train symbol
``{LORRY}``             Output a truck symbol
``{BUS}``               Output a bus symbol
``{PLANE}``             Output an aircraft
``{SHIP}``              Output a ship symbol
``{NORMAL_FONT}``       Switch to a normal font
``{TINY_FONT}``         Switch to a small font
``{BIG_FONT}``          Switch to a big font
``{MONO_FONT}``         Switch to a mono font
``{BLUE}``              Output following text in blue colour
``{SILVER}``            Output following text in silver colour
``{GOLD}``              Output following text in gold colour
``{RED}``               Output following text in red colour
``{PURPLE}``            Output following text in purple colour
``{LTBROWN}``           Output following text in light brown colour
``{ORANGE}``            Output following text in orange colour
``{GREEN}``             Output following text in green colour
``{YELLOW}``            Output following text in yellow colour
``{DKGREEN}``           Output following text in dark green colour
``{CREAM}``             Output following text in cream colour
``{BROWN}``             Output following text in brown colour
``{WHITE}``             Output following text in white colour
``{LTBLUE}``            Output following text in light blue colour
``{GRAY}``              Output following text in gray colour
``{DKBLUE}``            Output following text in dark blue colour
``{BLACK}``             Output following text in black colour
``{PUSH_COLOUR}``       Store the current colour
``{POP_COLOUR}``        Restore last saved colour
``{LRM}``               Left-to-right mark, zero-width character
``{RLM}``               Right-to-left mark, zero-width non-Arabic character
``{LRE}``               Treat the following text as embedded left-to-right
``{RLE}``               Treat the following text as embedded right-to-left
``{LRO}``               Force following characters to be treated as strong left-to-right characters
``{RLO}``               Force following characters to be treated as strong right-to-left characters
``{PDF}``               End the scope of the last ``{LRE}``, ``{RLE}``, ``{RLO}``, or ``{LRO}``
======================= ============================================================================

The final seven entries are used to handle directional formatting, used for
getting the right to left (RTL) string correct. See also `Directional
Formatting Code <http://www.unicode.org/unicode/reports/tr9/#Directional_Formatting_Codes>_`.

.. _pos-gamescript-string_commands:

Positional GameScript string commands
=====================================

====================== ====== ==============================================================
Command                Plural Effect
====================== ====== ==============================================================
``{STRING1}``             no  Replaced by {STRING} in the translation.
``{STRING2}``             no  Replaced by {STRING} in the translation.
``{STRING3}``             no  Replaced by {STRING} in the translation.
``{STRING4}``             no  Replaced by {STRING} in the translation.
``{STRING5}``             no  Replaced by {STRING} in the translation.
``{STRING6}``             no  Replaced by {STRING} in the translation.
``{STRING7}``             no  Replaced by {STRING} in the translation.
``{INDUSTRY}``            no  Industry, takes an industry number.
``{CARGO_LONG}``          no
``{CARGO_SHORT}``         no  Short cargo description, only ``### tons``, or ``### litres``.
``{CARGO_TINY}``          no  Tiny cargo description with only the amount.
``{CARGO_LIST}``          no
``{POWER}``               no
``{POWER_TO_WEIGHT}``     no
``{VOLUME_LONG}``         no
``{VOLUME_SHORT}``        no
``{WEIGHT_LONG}``         no
``{WEIGHT_SHORT}``        no
``{FORCE}``               no
``{VELOCITY}``            no
``{HEIGHT}``              no
``{DATE_TINY}``           no
``{DATE_SHORT}``          no
``{DATE_LONG}``           no
``{DATE_ISO}``            no
``{STRING}``              no
``{RAW_STRING}``          no  Replaced by {STRING} in the translation.
``{COMMA}``              yes  Number with comma.
``{DECIMAL}``            yes  Number with comma and fractional part.
``{NUM}``                yes  Signed number.
``{ZEROFILL_NUM}``       yes  Unsigned number with zero fill, e.g. ``02``.
``{BYTES}``              yes  Unsigned number with "bytes", i.e. ``1.02 MiB`` or ``123 KiB``.
``{HEX}``                yes  Hexadecimally printed number.
``{CURRENCY_LONG}``      yes
``{CURRENCY_SHORT}``     yes  Compact currency.
``{WAYPOINT}``            no
``{STATION}``             no
``{DEPOT}``               no
``{TOWN}``                no
``{GROUP}``               no
``{SIGN}``                no
``{ENGINE}``              no
``{VEHICLE}``             no
``{COMPANY}``             no
``{COMPANY_NUM}``         no
``{PRESIDENT_NAME}``      no
====================== ====== ==============================================================

