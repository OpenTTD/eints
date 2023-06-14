from .parameter_info import ParameterInfo

# Formatting (black) and validation (flake8) is disabled for this file.
# Please keep it nice and clean!
# fmt: off

P__ = (False, False)  # Parameter, not suitable for plural or gender
PP_ = (True,  False)  # Parameter suitable for plural
P_G = (False, True)   # Parameter suitable for gender
PPG = (True,  True)   # Parameter suitable for both plural and gender

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

    ParameterInfo("BLUE",           [], None, False, False ),
    ParameterInfo("SILVER",         [], None, False, False ),
    ParameterInfo("GOLD",           [], None, False, False ),
    ParameterInfo("RED",            [], None, False, False ),
    ParameterInfo("PURPLE",         [], None, False, False ),
    ParameterInfo("LTBROWN",        [], None, False, False ),
    ParameterInfo("ORANGE",         [], None, False, False ),
    ParameterInfo("GREEN",          [], None, False, False ),
    ParameterInfo("YELLOW",         [], None, False, False ),
    ParameterInfo("DKGREEN",        [], None, False, False ),
    ParameterInfo("CREAM",          [], None, False, False ),
    ParameterInfo("BROWN",          [], None, False, False ),
    ParameterInfo("WHITE",          [], None, False, False ),
    ParameterInfo("LTBLUE",         [], None, False, False ),
    ParameterInfo("GRAY",           [], None, False, False ),
    ParameterInfo("DKBLUE",         [], None, False, False ),
    ParameterInfo("BLACK",          [], None, False, False ),
    ParameterInfo("PUSH_COLOUR",    [], None, False, False ),
    ParameterInfo("POP_COLOUR",     [], None, False, False ),

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
    ParameterInfo("CARGO_SHORT",    [P_G, PP_], 1,    False, True ),  # short cargo description, only ### tons, or ### litres
    ParameterInfo("CARGO_TINY",     [P__, PP_], 1,    False, True ),  # tiny cargo description with only the amount
    ParameterInfo("CARGO_NAME",     [P_G],      None, True,  True ),
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

# Based on OpenTTD src/tables/strgen_tables.h r26050
_GS_PARAMETERS = [
    ParameterInfo("NORMAL_FONT",       [], None, False, True ),
    ParameterInfo("TINY_FONT",         [], None, False, True ),
    ParameterInfo("BIG_FONT",          [], None, False, True ),
    ParameterInfo("MONO_FONT",         [], None, False, True ),

    ParameterInfo("BLUE",              [],    None, False, False),
    ParameterInfo("SILVER",            [],    None, False, False),
    ParameterInfo("GOLD",              [],    None, False, False),
    ParameterInfo("RED",               [],    None, False, False),
    ParameterInfo("PURPLE",            [],    None, False, False),
    ParameterInfo("LTBROWN",           [],    None, False, False),
    ParameterInfo("ORANGE",            [],    None, False, False),
    ParameterInfo("GREEN",             [],    None, False, False),
    ParameterInfo("YELLOW",            [],    None, False, False),
    ParameterInfo("DKGREEN",           [],    None, False, False),
    ParameterInfo("CREAM",             [],    None, False, False),
    ParameterInfo("BROWN",             [],    None, False, False),
    ParameterInfo("WHITE",             [],    None, False, False),
    ParameterInfo("LTBLUE",            [],    None, False, False),
    ParameterInfo("GRAY",              [],    None, False, False),
    ParameterInfo("DKBLUE",            [],    None, False, False),
    ParameterInfo("BLACK",             [],    None, False, False),
    ParameterInfo("COLOUR",            [P__], None, False, True ),
    ParameterInfo("PUSH_COLOUR",       [],    None, False, False),
    ParameterInfo("POP_COLOUR",        [],    None, False, False),

    ParameterInfo("STRING1",           [P_G, PPG],                               None, True,  True,  "STRING"),
    ParameterInfo("STRING2",           [P_G, PPG, PPG],                          None, True,  True,  "STRING"),
    ParameterInfo("STRING3",           [P_G, PPG, PPG, PPG],                     None, True,  True,  "STRING"),
    ParameterInfo("STRING4",           [P_G, PPG, PPG, PPG, PPG],                None, True,  True,  "STRING"),
    ParameterInfo("STRING5",           [P_G, PPG, PPG, PPG, PPG, PPG],           None, True,  True,  "STRING"),
    ParameterInfo("STRING6",           [P_G, PPG, PPG, PPG, PPG, PPG, PPG],      None, True,  True,  "STRING"),
    ParameterInfo("STRING7",           [P_G, PPG, PPG, PPG, PPG, PPG, PPG, PPG], None, True,  True,  "STRING"),

    ParameterInfo("INDUSTRY",          [P_G],      None, True,  True ),  # takes an industry number.
    ParameterInfo("CARGO_LONG",        [P_G, PP_], 1,    False, True ),
    ParameterInfo("CARGO_SHORT",       [P_G, PP_], 1,    False, True ),  # short cargo description, only ### tons, or ### litres
    ParameterInfo("CARGO_TINY",        [P__, PP_], 1,    False, True ),  # tiny cargo description with only the amount
    ParameterInfo("CARGO_LIST",        [P__],      None, True,  True ),
    ParameterInfo("POWER",             [PP_],      0,    False, True ),
    ParameterInfo("POWER_TO_WEIGHT",   [PP_],      0,    False, True ),
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

    ParameterInfo("COMMA",             [PP_],      0,    False, True ),  # Number with comma
    ParameterInfo("DECIMAL",           [PP_, P__], 0,    False, True ),  # Number with comma and fractional part.
    ParameterInfo("NUM",               [PP_],      0,    False, True ),  # Signed number
    ParameterInfo("ZEROFILL_NUM",      [PP_, P__], 0,    False, True ),  # Unsigned number with zero fill, e.g. "02".
    ParameterInfo("BYTES",             [PP_],      0,    False, True ),  # Unsigned number with "bytes", i.e. "1.02 MiB or 123 KiB"
    ParameterInfo("HEX",               [PP_],      0,    False, True ),  # Hexadecimally printed number

    ParameterInfo("CURRENCY_LONG",     [PP_],      0,    False, True ),
    ParameterInfo("CURRENCY_SHORT",    [PP_],      0,    False, True ),  # compact currency

    ParameterInfo("WAYPOINT",          [P_G],      None, False, True ),  # waypoint name
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

# Based on OpenTTD src/tables/strgen_tables.h r26050
_OPENTTD_PARAMETERS = [
    # Some string parameters are only allowed in the OpenTTD project.
    # While they technically also work in Game Scripts, disencourage the usage.
    # This also includes the "sprite" characters.
    ParameterInfo("REV",               [],    None, False, True ),
    ParameterInfo("STATION_FEATURES",  [P__], None, False, True ),  # station features string, icons of the features
    ParameterInfo("UP_ARROW",          [],    None, False, True ),
    ParameterInfo("SMALL_UP_ARROW",    [],    None, False, True ),
    ParameterInfo("SMALL_DOWN_ARROW",  [],    None, False, True ),
    ParameterInfo("DOWN_ARROW",        [],    None, False, True ),
    ParameterInfo("CHECKMARK",         [],    None, False, True ),
    ParameterInfo("CROSS",             [],    None, False, True ),
    ParameterInfo("RIGHT_ARROW",       [],    None, False, False),  # left/right arrows are not critical due to LTR/RTL languages
    ParameterInfo("SMALL_LEFT_ARROW",  [],    None, False, False),
    ParameterInfo("SMALL_RIGHT_ARROW", [],    None, False, False),
]

OPENTTD_PARAMETERS = dict((x.literal, x) for x in _OPENTTD_PARAMETERS)
OPENTTD_PARAMETERS.update((x.literal, x) for x in _GS_PARAMETERS)

NL_PARAMETER = ParameterInfo("", [], None, False, False)
CURLY_PARAMETER = ParameterInfo("{", [], None, False, False)
