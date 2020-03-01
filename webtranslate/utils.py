from webtranslate import data, bottle
from webtranslate.newgrf import language_file
import re

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

def template(tpl, **kwargs):
    """
    Build HTML from template

    @param tpl: Templatename
    @type  tpl: C{str}

    @param kwargs: Template parameters
    @type  kwargs: C{dict}
    """

    messages = kwargs.setdefault("messages", [])

    if "message" in kwargs:
        messages.append({'content': kwargs.get("message"), 'class': kwargs.get('message_class', 'info')})

    query = bottle.request.query
    if len(query.get('message', '')) > 0:
        messages.append({'content': query.get("message"), 'class': query.get('message_class', 'info')})

    # message classes map to bootstrap css alert style names. n.b. default bootstrap alert is yellow (warning), but our default is blue (info)
    message_classes = {'info': 'alert-info',
                       'success': 'alert-success',
                       'warning':'',
                       'error': 'alert-error'}

    for msg in messages:
        msg['class'] = message_classes.get(msg.get('class', 'info'), '')

    return bottle.template(tpl, **kwargs)

def verify_name(name, name_type, is_identifier):
    """
    Check whether a provided name is sane enough to accept as project name.

    @param name: Proposed new project name.
    @type  name: C{str}

    @param name_type: Type of name processed
    @type  name_type: C{str}

    @param is_identifier: Whether the name shall be a valid identifier to be used in URLs.
    @type  is_identifier: C{bool}

    @return: Whether the name is acceptable.
    @rtype:  C{str} with an error description, or C{None} if all is well.
    """
    if not name:
        return "{} missing".format(name_type)
    if is_identifier:
        if not re.match('[-A-Za-z0-9_]+$', name):
            return "{} can only contain characters A-Z, a-z, 0-9, dash (-) and underscore (_)".format(name_type)
    else:
        if len(name) == 0:
            return "{} may not be empty".format(name_type)
    return None

def verify_url(url):
    """
    Check whether a provided URL is sane enough to accept as project reference.

    @param url: Proposed new url.
    @type  url: C{str}

    @return: Whether the url is acceptable.
    @rtype:  C{str} with an error description, or C{None} if all is well.

    @todo: Improve project URL checking.
    """
    if url == '':
        return None

    if url.startswith('http://') or url.startswith('https://'):
        return None # XXX This is a bit too much trust perhaps.

    return "Incorrect url"

def create_displayed_base_text(pdata, text):
    """
    Construct the base language string to display to the user. In particular,
    transform the string commands that are available in the base language only.

    @param pdata: Project data.
    @type  pdata: L{Project}

    @param text: Text to display.
    @type  text: L{Text}

    @return: String to display.
    @rtype:  C{str}
    """
    text = text.text
    blng = pdata.get_base_language()
    if blng is None: return text
    str_info = language_file.check_string(pdata.projtype, text, True, None, blng, True)
    if str_info.has_error or str_info.pieces is None: return text
    return str_info.get_translation_text()

def lang_needs_fixing(overview):
    """
    Check whether a language needs fixing.

    @param overview: Number of strings per state, as in ProjectMetaData.overview.
    @type  overview: C{list} of C{int}

    @return: Whether the language needs fixing.
    @rtype:  C{bool}
    """
    return overview[data.OUT_OF_DATE] != 0 or overview[data.INVALID] != 0 or overview[data.MISSING] != 0

def lang_is_empty(overview):
    """
    Check whether a language is complete empty, that is not even missing strings.

    @param overview: Number of strings per state, as in ProjectMetaData.overview.
    @type  overview: C{list} of C{int}

    @return: Whether the language is empty.
    @rtype:  C{bool}
    """
    return sum(overview) == 0

def redirect(path, **kwargs):
    """
    Quotes and encodes an URL and sends a redirect response.

    @param path: Route pattern.
    @type  path: C{str}

    @param kwargs: Route and URL parameters.
    @type  kwargs: C{dict} of C{str} to C{str}
    """
    u = bottle.url(path, **kwargs)
    bottle.redirect(u)
