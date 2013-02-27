from webtranslate import data

def get_datetime_now_formatted():
    """
    Output a string denoting 'now' in time,
    useful for user messages when creating or updating objects

    @return: A string denoting 'now' in time (in UTC).
    @rtype:  C{str}
    """
    stamp = data.make_stamp()
    return str(stamp)

class TimeDescription:
    """
    @ivar unit_name: Name of the time measuring unit.
    @type unit_name: C{str}

    @ivar name_fixed: Name is a fixed string (ie no number prefix needed).
    @type name_fixed: C{bool}

    @ivar unit_size: Number of seconds that one unit lasts.
    @type unit_size: C{int}

    @ivar max_count: Maximum number of units that should be counted.
    @type max_count: C{int}
    """
    def __init__(self, name, fixed, size, count):
        self.unit_name = name
        self.name_fixed = fixed
        self.unit_size = size
        self.max_count = count

    def to_string(self, difference):
        """
        Create the time description.

        @param difference: Number of seconds time delta to describe.
        @type  difference: C{int}

        @return: Short description of the difference.
        @rtype:  C{str}
        """
        if self.name_fixed: return self.unit_name

        difference = difference // self.unit_size
        return "{:d} {}".format(difference, self.unit_name)

# I am aware the unit sizes are not exact.
# If you consider the difference relevant, max_count is not big enough for you.
time_descriptions = [TimeDescription("Just now", True,              1, 3),
                     TimeDescription("seconds",  False,             1, 59),
                     TimeDescription("minutes",  False,            60, 59),
                     TimeDescription("hours",    False,         60*60, 48),
                     TimeDescription("days",     False,      24*60*60, 14),
                     TimeDescription("weeks",    False,    7*24*60*60, 6),
                     TimeDescription("months",   False, 30*7*24*60*60, 24),
                     TimeDescription("years",    False, 52*7*24*60*60, 10000)]

def get_relative_time(old_stamp, now):
    """
    Get a description of the relative time between stamps L{old_stamp} and L{now}.

    @param old_stamp: Time stamp to describe.
    @type  old_stamp: L{Stamp}

    @param now: Current time.
    @type  now: L{Stamp}

    @return: Short textual description how much time has passed between both stamps.
    @rtype:  C{str}
    """
    difference = now.seconds - old_stamp.seconds

    i = 0
    td = time_descriptions[i]
    while i + 1 < len(time_descriptions):
        if difference < td.unit_size * td.max_count: break
        i = i + 1
        td = time_descriptions[i]

    return td.to_string(difference)


def get_messages(request):
    """
    Can return an arbitrary number of messages from this method, passed via a number of methods.
    1. Query string can pass one message.
    2. UNFINISHED. Pass via template (number of messages unknown).
    Messages can have optional classes, which changes appearance
    """

    # message classes map to bootstrap css alert style names. n.b. default bootstrap alert is yellow (warning), but our default is blue (info)
    message_classes = {'info': 'alert-info',
                       'success': 'alert-success',
                       'warning':'',
                       'error': 'alert-error'}

    messages = []
    if len(request.query.get('message', '')) > 0:
        message = {}
        message['content'] = request.query.get('message', '')
        message['class'] = message_classes[request.query.get('message_class', 'info')]
        messages.append(message)

    if len(messages) > 0:
        return messages
    else:
        return None

def get_status_definition_strings():
    status_definitions = {'UNKNOWN': {'title': 'Unknown', 'description': 'The state of the translation was not decidable'},
                          'UP_TO_DATE': {'title': 'Correct', 'description': 'The string is technically correct and up to date'},
                          'OUT_OF_DATE': {'title': 'Outdated', 'description': 'A valid translation exists, but it needs review as a newer base language text exists'},
                          'INVALID': {'title': 'Invalid', 'description': 'A translation exists, but its string parameters do not match with the base language'},
                          'MISSING_OK': {'title': 'Missing', 'description': 'No translation could be found'}}
    return status_definitions
